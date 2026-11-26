"""Workspace cleanup preserves open parent defects and historical evidence."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("workspace_audit", ROOT / "scripts/audit-workspace-tasks.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class WorkspaceTaskTests(unittest.TestCase):
    def fixture(self):
        return ("# Current\n## Suggested execution order\n1. Work\n"
                "- [ ] **WEB-115 / WEB-014 / WP16-004** - original defect\n"
                "## Checklist change ledger\n"
                "[history](workspace-task-history-2026-11-20.md)\n")

    def test_exact_ledger_heading_not_string_character_split(self):
        active, ledger = AUDIT.split_ledger("# Current\n- [ ] **WEB-115**\n## Checklist change ledger\n- [x] **WEB-023**\n")
        self.assertIn("WEB-115", active)
        self.assertIn("WEB-023", ledger)

    def test_unknown_or_closed_root_task_refuses(self):
        with self.assertRaises(ValueError):
            AUDIT.check_index(self.fixture(), {"WEB-115"}, {"WEB-014", "WP16-004"})

    def test_completed_subgate_never_closes_open_parent(self):
        source = "- [ ] **WEB-115**\n## Checklist change ledger\n- [x] **WEB-115** diagnostic subgate only\n"
        opened, closed = AUDIT.canonical_status(source)
        self.assertIn("WEB-115", opened)
        self.assertIn("WEB-115", closed)

    def test_active_completion_is_invalid(self):
        with self.assertRaises(ValueError):
            AUDIT.canonical_status("- [x] **WEB-115**\n## Checklist change ledger\n")

    def test_history_and_single_order_required(self):
        for text in (self.fixture().replace("workspace-task-history-2026-11-20.md", "lost.md"),
                     self.fixture().replace("## Checklist change ledger", "## Suggested execution order\n## Checklist change ledger"),
                     self.fixture().replace("# Current", "Current2026-11-19: old pending note")):
            with self.assertRaises(ValueError):
                AUDIT.check_index(text, {"WEB-115", "WEB-014", "WP16-004"}, set())

    def test_ledger_execution_order_is_history_not_active(self):
        result = AUDIT.check_index(self.fixture() + "\n## Suggested execution order\n",
                                  {"WEB-115", "WEB-014", "WP16-004"}, set())
        self.assertEqual(result["activeRows"], 1)

    def test_read_only_audit_accepts_open_composite_parent(self):
        result = AUDIT.check_index(self.fixture(), {"WEB-115", "WEB-014", "WP16-004"}, set())
        self.assertEqual(result["activeRows"], 1)
        self.assertTrue(result["readOnly"])
        self.assertFalse(result["changedAcceptanceOrCheckboxes"])

    def test_broken_or_escaping_link_refuses(self):
        with tempfile.TemporaryDirectory() as folder:
            for target in ("absent.md", "../outside.md"):
                with self.assertRaises(ValueError):
                    AUDIT.check_links("[evidence](" + target + ")", Path(folder))
    def test_starred_observation_is_not_active_or_complete(self):
        source=self.fixture().replace('[ ]','[*]')
        pending,complete=AUDIT.canonical_status(source)
        flagged=AUDIT.flagged_status(source)
        self.assertEqual(pending,set());self.assertEqual(complete,set())
        result=AUDIT.check_index(source,pending,complete,flagged)
        self.assertEqual(result['activeRows'],0);self.assertEqual(result['flaggedRows'],1)
        self.assertEqual(set(result['flaggedIds']),{'WEB-115','WEB-014','WP16-004'})
    def test_star_cannot_silently_hide_an_open_owner(self):
        with self.assertRaises(ValueError):
            AUDIT.check_index(self.fixture().replace('[ ]','[*]'),{'WEB-115','WEB-014','WP16-004'},set())
    def test_same_id_cannot_be_both_active_and_starred(self):
        source=self.fixture().replace('## Checklist change ledger','- [*] **WEB-115**\n## Checklist change ledger')
        with self.assertRaises(ValueError):
            AUDIT.check_index(source,{'WEB-115','WEB-014','WP16-004'},set(),{'WEB-115'})


if __name__ == "__main__":
    unittest.main()
