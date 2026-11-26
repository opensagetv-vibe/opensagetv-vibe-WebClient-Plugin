# Stock DVD profile Apply boundary (WEB-108 / WEB-021)

The browser cannot reconfigure the server-side DVD MPEG-PS converter through
HTML video.currentTime or an ordinary recording byte seek. The existing DVD
MiniClient wire deliberately leaves navigation with stock MiniDVDPlayer; a
browser-local SEEK cannot reconstruct its authored NAV, audio and SPU state.
Changing a browser quality preference alone affects only future source epochs.
These client-only alternatives therefore cannot satisfy an explicit active
DVD encoder/profile change.

The existing owning Web Client plugin now uses the public SageTV API instead:

1. Resolve this exact local browser MiniClient UI, never another client.
2. Require loaded DVD feature playback, no DVD menu/options dialog, a valid
   current title/file, a finite non-negative native title clock and normal rate.
3. Recheck source/title/modal state and atomically validate the exact current
   HLS producer/native generation before staging its per-client profile.
4. Submit one public Seek to GetRawMediaTime. Browser-relative time is ignored;
   stock Core owns the resulting FLUSH, new Push/NAV epoch and converter input.
5. The normal replacement video event attaches the browser after real output.

No media/bridge lock is held across the public Seek. No MCP, Client Extension,
new Core event, sage.* class, bytecode change, shared profile mutation or
ordinary-file fallback is used. An unknown submission outcome is not replayed;
another Apply for that same producer is refused until its generation changes.
Read failures and unsupported context/menu/rate states leave the profile and
playback untouched. A successfully submitted request is not itself presented
video proof, and the UI reports it as submitted rather than already displayed.

Paused stock DVD processing may defer both FLUSH and new Push until Resume.
Apply never sends Play to obtain frames. The replacement must be verified only
after the user's normal Resume, while pause intent remains unchanged beforehand.
Save remains non-disruptive and takes effect at the next native DVD source epoch.
Automatic slider Apply for DVD remains off; active replacement is explicit.

Acceptance distinguishes requested700kbps, actual encoder argument `-b:v 700k`,
and actual encoded480p raster from browser display dimensions. For this DVD,
WebKit reports720x405 display after sample-aspect correction even though the
encoded stream is720x480. This is not failure to honor the height limit.
Clock/pictures must continue for eight seconds after replacement; API receipts,
old cached frames and a temporary stock seek guess are not sufficient.

Local tests are public-API mocks, actual stock-wire runtime, and production DOM
checks. Desktop Chrome/WebKit field results are recorded separately in
artifacts/results/WEB-108/RESULT.md; none substitutes for physical iPhone,
all-disc, acoustic, Windows or high-speed reverse/256x scan acceptance.
