# P15 stock-server contract boundary

2026-11-20. User requests completion of P15–P17; the standing stock-server and
publication policies still apply. This document records supported alternatives,
not permission to replace Core or a claim that private Core features now exist.

| Task / original goal | Stock-compatible implementation and boundary |
| --- | --- |
| WP15-001 capability negotiation | Existing optional Client Extension revision4 `web-mpegps-v1` per-load challenge, exact local UI, no challenge in reports. Missing/off/older/late services leave native DVD unchanged. Private `DVD_DISC_*` GET is empty; unsupported extension SET now returns failure rather than a false success. |
| WP15-002 `dvd_mpegts_v1` / `transformed_main_feature` | **Unavailable in this Web profile.** The commissioned representation is authored native MPEG-PS, converted once for HTML5 by the Web/MIM owner. The companion's Android transformed profile is not acknowledged by this browser. No verified browser transformed-input consumer exists; copying its name would not implement it. Keep this row open, not PASS. |
| WP15-003 menu/preview/hybrid policy | Native authored menus remain the default. Optional current-load Start feature/Resume actions reuse the companion navigator; its administrator options Start Longest DVD Title / Skip DVD Previews to Root are separate plugin policies, not Web global-property writes. Private hybrid transport options remain unexposed. No seamless transformed/native transition is claimed. |
| WP15-004 richer metadata / rate | Existing public API source/growing state, bounded stream probes and source-owned requested/accepted/displayed clock snapshot; forward0.5–2x uses the implemented media command/browser path. Remove unimplemented private `MEDIA_STATE_URL=TRUE` advertisement. No guessed STC, native reverse/high-rate or frame-step claim. |
| WP15-005 packaging / rollback | Stock WAR contains no Sage Core classes, native replacements, FFmpeg implementation or companion implementation. Required platform FFmpeg/MIM stays separately manager-installed; Client Extension remains optional/off by default. No Core/provider release is created. |

## Why use the existing companion only for the optional DVD actions?

Ordinary authored DVD, captions, seek and rate work without it. Stock's public
DVD menu/seek controls do not expose a per-load longest-title catalog/bookmark
transaction to this browser. The already-qualified companion supplies that
bounded public-plugin contract; the Web Client neither substitutes MCP controls
for production nor creates another navigator/transcoder. No new server plugin
or Core modifications are needed for this work.

## Affected qualification

`P15StockContractsSmoke` checks17 current production contracts. The real TCP
`MiniClientProtocolSmoke` queries all unsupported names and verifies negative
SET receipts before normal first-frame/resize/input traffic. Existing
`CompanionDvdSmoke` checks missing/older/current/stale/slow service behavior,
secret-safe diagnostics and one-shot unknown mutation outcomes. P12 rate and
native DVD protocol tests remain required. These are unit/synthetic-wire tests,
not physical phone proof.

Run actual installed stock Linux optional/native DVD checks separately; record
their precise result and restored settings in `artifacts/results/WP15-001/`.
Reuse unaffected prior phone/matrix evidence. The two user-starred P16
observations remain possibly fixed/not repeatable, not verified corrections.

P17 remote commit/push/tag/release remains held pending explicit approval.
The original3.2.4 rollback requirement was removed by the user, not passed.
Local deterministic build/package checks are not remote publication.
