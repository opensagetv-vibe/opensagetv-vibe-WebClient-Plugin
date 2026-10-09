# OpenSageTV Vibe Web Client Plugin instructions

## Task fix and server-boundary policy

Apply this policy to every task workflow, including dependency fixes across
Vibe repositories. Fix and test necessary plugins and update the test-server
plugin without asking again solely for repository-boundary approval.

Prefer the Android client, then a stock-compatible plugin. Change non-stock
`.232` Core only for a proven production defect that neither can correct;
document the API gap and alternatives, keep optional negotiation and safe
stock/older-client fallback, and run affected compatibility tests. Never patch
Core merely to simplify testing.

Stock `.175` installation changes are limited to plugin installation/update.
Do not modify its stock Sage.jar, stock FFmpeg, Core binaries, or server
installation/configuration files. Preserve user settings, recordings and
unrelated clients; reversible supported SageTV playback APIs remain allowed.

Non-stock `.232` restarts are authorized for task updates without asking
again; coordinate them with active test guards and preserve data/settings.
  Always ask the user before restarting stock `.175`, even when it appears idle,
  unless an explicit user-granted bounded restart window is active. Record
  its UTC expiry in the task/handoff, and check expiry and revocation before
  every restart. After expiry or revocation, ask again; stock files stay protected.

Update owning TASKS.md, linked dependencies and the workspace suggested order
as work changes; move completed checkoffs into the checklist change ledger.
Test only affected gates, preserve unrelated completed matrices, and do not
stop independent authorized work for a status question or a dependency-only
permission request. Unrelated work, publication, destructive actions and
interruption of recordings/other users still require their own authority.

Read `HANDOFF.md`, `README.md`, `TASKS.md`, `WORKFLOW.md`, and the directly
relevant parity document before changing code. Historical Markdown under
`docs/` is evidence and must not be silently rewritten as current proof.

Keep the plugin compatible with an unmodified stock SageTV `Sage.jar`. For
transcoding, depend on the platform-matching OpenSageTV Vibe FFmpeg Plugin and
its `SageTVTranscoder` bridge. Never replace SageTV's stock `ffmpeg` and never
bundle FFmpeg/MIM binaries in this repository.

Use the sibling `opensagetv-vibe-build-env` through `dev.cmd` or `dev.sh`.
Physical commissioning on `.232` is explicit and must preserve server data,
configuration, recordings, and unrelated plugins. Do not publish this plugin
or a public manifest until the user gives final approval.

For new test controls, use the stock-compatible Core MCP plugin and supported
SageTV APIs before considering a Core change. Generated, simulated, browser,
and physical evidence must be labeled accurately.

Release validation is impact-based: rerun only gates the release changes could
affect. Do not repeat unrelated completed gates. Run the full gate suite only
when the user explicitly requests it or a broad dependency/architecture change
requires it, and document that reason and scope.

## Pre-commit task-list maintenance

Immediately before every repository commit, clean `TASKS.md`: move every
completed `[x]` item out of the active task sections and into
`## Checklist change ledger`. Preserve stable IDs, acceptance evidence, order,
and enough source/parent context to understand the result. Never delete
completion history. Active task sections must contain unchecked work only;
checked boxes may appear only inside the checklist change ledger. Regenerate
the project manifest when the repository tracks one.
