#!/usr/bin/env python3
"""Read-only workspace index/ledger audit; never infer or write completion."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parent.parent
LEDGER = "## Checklist change ledger"
BOX = re.compile(r"^\s*- \[([ x*\-])\] (.*)$", re.M)
ID = re.compile(r"\b(?:[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3})\b")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def split_ledger(text: str) -> tuple[str, str]:
    parts = re.split(r"^## Checklist change ledger\s*$", text, maxsplit=1, flags=re.M)
    if len(parts) != 2:
        raise ValueError("Missing unambiguous checklist change ledger")
    return parts[0], parts[1]


def canonical_status(text: str) -> tuple[set[str], set[str]]:
    active, ledger = split_ledger(text)
    if any(m[1] == "x" for m in BOX.finditer(active)):
        raise ValueError("Completed checkbox remains in active sections")
    pending = {key for m in BOX.finditer(active) if m[1] == " " for key in ID.findall(m[2])}
    complete = {key for m in BOX.finditer(ledger) if m[1] == "x" for key in ID.findall(m[2])}
    return pending, complete


def flagged_status(text: str) -> set[str]:
    active, _ = split_ledger(text)
    return {key for m in BOX.finditer(active) if m[1] == "*" for key in ID.findall(m[2])}


def check_index(text: str, pending: set[str], complete: set[str], flagged: set[str] | None = None) -> dict:
    active, ledger = split_ledger(text)
    if any(m[1] == "x" for m in BOX.finditer(active)):
        raise ValueError("Workspace completion outside ledger")
    rows = [m[2] for m in BOX.finditer(active) if m[1] == " "]
    ids = [key for row in rows for key in ID.findall(row)]
    starred = [m[2] for m in BOX.finditer(active) if m[1] == "*"]
    flagged_ids = [key for row in starred for key in ID.findall(row)]
    if len(ids + flagged_ids) != len(set(ids + flagged_ids)):
        raise ValueError("Duplicate active workspace task ID")
    for key in ids:
        if key not in pending:
            raise ValueError("Workspace task not open in its canonical owner: " + key)
    for key in flagged_ids:
        if key not in (flagged or set()):
            raise ValueError("Workspace observation not starred in its canonical owner: " + key)
    # A checked child/sub-gate can coexist with its genuinely open parent.
    # Never infer that a parent is done from a historical completion mention.
    if active.count("## Suggested execution order") != 1:
        raise ValueError("Missing/duplicated current execution order")
    if re.search(r"^Current\d{4}|^RESUMED\d{4}|^Final local continuation", active, re.M):
        raise ValueError("Historical checkpoint was prepended to current index")
    if "workspace-task-history-2026-11-20.md" not in ledger:
        raise ValueError("Original workspace history link missing")
    return {"activeRows": len(rows), "activeIds": ids,
            "flaggedRows": len(starred), "flaggedIds": flagged_ids,
            "completedIdsObserved": len(complete), "readOnly": True,
            "changedAcceptanceOrCheckboxes": False}


def check_links(text: str, root: Path) -> int:
    count = 0
    for raw in LINK.findall(text):
        if raw.startswith(("https://", "http://", "#")):
            continue
        target = raw.split("#", 1)[0]
        candidate = root / target
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root.resolve()):
            raise ValueError("Link escapes workspace")
        # Refuse symlink/junction traversal, including existing ancestors.
        for part in (candidate, *candidate.parents):
            if part == root:
                break
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError("Reparse link target")
        if not candidate.is_file():
            raise ValueError("Broken task/evidence link: " + target)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    pending: set[str] = set()
    complete: set[str] = set()
    flagged: set[str] = set()
    owners = 0
    for directory in sorted((WORKSPACE / "projects").iterdir()):
        path = directory / "TASKS.md"
        if not path.is_file():
            path = directory / "TASK.MD"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        # Older independent projects without this ledger are reported separately;
        # they are not silently rewritten by a current Web dependency audit.
        if not re.search(r"^## Checklist change ledger\s*$", text, re.M):
            continue
        opened, closed = canonical_status(text)
        pending.update(opened)
        complete.update(closed)
        flagged.update(flagged_status(text))
        owners += 1
    text = (WORKSPACE / "task.md").read_text(encoding="utf-8-sig")
    result = check_index(text, pending, complete, flagged)
    result.update(passed=True, ownersAudited=owners,
                  localLinksChecked=check_links(text, WORKSPACE))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
