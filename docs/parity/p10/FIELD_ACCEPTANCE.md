# P10 Field acceptance checklist

Current2026-11-19: WP10-004 explicit nonfirst fixture83871 now passes actual
stock232 WebKit030512/Chromium031017 five rows each, title2/native11978ms/
chapter1/new pictures/root and independent explicit IFO probe11.995s/three
title-relative chapters. WEB091 corrects installed-plugin ffprobe lookup;
normal-manager025903/stock20 unchanged. Compact WP10-004RESULT preserves
setup failures, exact package and boundaries. Checklist below remains test
guidance; do not read its old pending language as current absence of this proof.

Use an unchanged SageTV library/database backup before any metadata repair experiment. Normal P10 inspection is read-only and requires no library changes.

- Verify a VIDEO_TS MediaFile and a parent directory containing VIDEO_TS are classified as native DVD.
- Verify an ISO that previously failed mounting reports the stock-server ISO mount stage rather than a generic decoder failure.
- Verify two different SageTV files with the same basename cannot be cross-selected after a mapped-root/path change.
- Verify spaces, literal `+`, Unicode and the server's actual Windows/UNC or POSIX path style resolve to the intended MediaFile.
- On a multi-title DVD with extras, request the known intended title explicitly and compare reported duration/chapters with the authored disc. Do not infer “main feature” from title number or VOB size.
- Verify movie-only capability is labeled non-interactive and disappears/fails clearly if a test FFmpeg without `dvdvideo`/libdvdread/libdvdnav is configured.
- If SageTV reports an impossible imported duration (for example 1 ms), confirm the plugin reports it as metadata health and does not seek, rewrite the library, clear history or reindex automatically.
- Verify VOB/MKV are shown as ordinary media, and BDMV/Blu-ray is shown as unsupported/pending disc scope.
