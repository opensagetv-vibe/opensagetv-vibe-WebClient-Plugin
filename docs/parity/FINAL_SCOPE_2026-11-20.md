# Stock HTML5 scope reconciliation — 2026-11-20 UTC

Installed development build: normal-manager `3.3.0.20261120.053814`,
WAR `9b4c471857227b557cd0462cd74a678dedb82e882330cc8f92b5da66a793e831`.
Stock Linux `.232`, protected Core unchanged; FFmpeg Plugin0.1.27/MIM0.4.14.
This is an evidence reconciliation, not a new release or an all-format claim.
The five user-removed file/equipment tests are excluded, never counted as PASS.

## Completed inventory and portable adaptation

WEB-020 inventory is current: Android0.5.115,269 preferences, no changed source
hashes, additions, removals or preference changes in the live sibling audit.
Every recorded preference has a screen, key, group and adaptation. The current
feature matrix supplies each group's implemented equivalent or platform limit.
No further portable implementation gap is identified in this reviewed scope.

WEB-021 portable gaps now have the following dispositions:

| Requirement | Actual disposition and evidence |
| --- | --- |
| Generated A/V calibration and offsets | Normal FFmpeg/browser path,25ms UI/±4s range, output/restoration tests; WEB023 phone calibration and P12 records. Acoustic acceptance removed, not certified. |
| Gamepad modal/editable ownership | Portable input policy implemented and unit-tested; physical controller test removed by user. |
| Software deinterlace selection | Explicit YADIF/BWDIF profiles and strict Copy rejection already implemented; P12 and CURRENT_FEATURE_MATRIX evidence. Browser hardware decoding remains opaque. |
| DVD Time Scroll, held chapters and transport search | WEB055/108/113/117, actual stock-STV/SageMC in both host engines and native iPhone. Repeated search retains producer until accept; Play/Back cancels. |
| Active DVD quality Apply | WEB108 desktop and WEB117 actual phone700k/480p/QSV, moving pictures/clock and exact profile restoration. |
| Native256x/reverse/frame-step | Not exposed as capabilities. HTMLMediaElement cannot guarantee these; stock-safe Time Scroll search is the qualified equivalent, not a fake decoded rate. |

Fresh affected offline checks:23 input groups,99 playback groups,20 experience
groups and11 remaining-field safety contracts pass. No runtime source changed
in this reconciliation. Inventory completion is NOT universal physical parity;
WEB115/DVD and caption-tail historical failures remain independently open.

## Delivery matrix disposition (WP16-002)

The criterion explicitly permits supported combinations to pass and unavailable
combinations to remain labeled. It does not require inventing backend support.

| Backend/path | Disposition |
| --- | --- |
| Chromium HLS/MSE and TS/MSE | Actual cold/warm moving output and real minimized/restore pass. |
| Linux WebKit HLS/MSE and TS/MSE | Actual cold/warm moving output pass. Its real X11 minimized window does not expose document.hidden, so hidden-media qualification is UNAVAILABLE on this backend. |
| Linux WebKit native HLS | UNSUPPORTED by the measured MIME/decoder backend; not an iPhone failure. |
| Chromium explicit Native HLS | Measured native rejection; permitted same-producer MSE fallback passes. Strict native rejection is truthful, not a native PASS. |
| Physical Safari native HLS | Separate actual WEB023 native playback, Home/background/reconnect, caption and DVD proof; not inferred from desktop WebKit. |

Evidence: artifacts/results/WP16-002/RESULT.md, WEB096/RESULT.md,
WEB109/RESULT.md and WEB023/IPHONE_LIFECYCLE_LAYOUT.md (under artifacts/results).
WP16-002 closes with these explicit backend limitations, not blanket support.
Final cellular/VPN experience remains WEB023 and is not closed by this table.

## Bounded stress qualification (WP16-006)

User removed multi-hour elapsed testing. Reuse, rather than replay, qualified
resource and ownership gates unaffected by later local DVD input/render fixes:

- WP16-006/SUSTAINED.md:600.032s actual late-offset playback,17,977 new frames,
  zero recoveries/clock regressions,21 resource samples and post-Stop decrease.
- WEB102/RESULT.md:22 actual isolated disk-pressure/process-retirement checks;
  private bounded sandbox, never fill the real server disk.
- WP16-006/OWN-01.md and WEB106/RESULT.md:real concurrent native/public clients,
  source/seek/caption/Stop isolation and unknown-activity refusal.
- WEB104/105/117 and WEB023 current results:affected profile/recovery, actual
  seek/search/chapter/teardown and real105s still/return scopes.
- Malformed-input, source epoch, stale callbacks, cancellation and bounded
  recovery are separately covered by production unit/integration tests.

These close the requested bounded stress matrix, not unlimited leak freedom,
all-service/all-disc certification, receiver acoustics or a three-hour soak.
Unclassified old decoder/query failures remain recorded in their owning issue
evidence; no retrospective fix is inferred from subsequent passes.

## Requirements intentionally still distinct

WP16-007's acceptance/issue disposition is complete by listing the following
unresolved rows explicitly, as its original criterion permits. This is not
closure of the defects, GitHub issues or final phone acceptance.

- WEB115/DVD matrix:original024848Z pre-search chapter-start stall needs a
  comparable recurrence with producer/element/buffer diagnostics. Repeated
  successful replacements are not a repaired-defect PASS.
- WP16-003 caption matrix:original203329 native caption-tail stall is not
  proven fixed by later seeks/EOF/reconnect passes.
- WEB023 final physical/VPN scope and WP16-007 issue disposition inherit only
  applicable remaining requirements, never the five waived equipment/files.
- Optional WP15 extended-Core tasks stay deferred under stock-only authority.
- WP17-006 remains publication-held. No commit/push/tag/release authorized.
