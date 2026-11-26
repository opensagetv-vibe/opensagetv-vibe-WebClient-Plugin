# Portrait browser deck — WEB-074

Portrait mobile now presents one full-width, aspect-preserving TV surface
(normally16:9) above a separate browser deck. It does not enlarge the native
STV vertically to consume the phone. Automatic native graphics retain bounded
high-DPI rasterization and landscape proportions, including low-density narrow
phones where the old240px logical-height minimum otherwise distorted aspect.
Fixed UI choices and explicit UI query dimensions remain independent.

In the iPhone Home Screen app, portrait reserves `safe-area-inset-top` above
the entire stage. The translucent system status bar/notch therefore stays on
black, not over native STV graphics or video. The visible Safari toolbar owns
its own inset and landscape retains its existing full-screen layout. Both
layers continue to share exactly the same stage/pointer transform; the list
viewport absorbs the reduced available height rather than stretching video.

App settings → **Portrait top spacing (px)** adds user-adjustable clearance
below that automatic inset (default24px, range0..160). It applies immediately
to the common STV/video stage in portrait, including ordinary Safari, without
restarting playback or changing transcoding. Zero removes only this additional
space, not the Home Screen system inset. Landscape ignores the setting. The
browser remembers it and includes it in saved-default profile export/import;
missing older profile fields preserve the current value.

App settings also has **Reload webpage**, separate from Reconnect and content
list Refresh. It reloads this same URL without clearing browser preferences.
If a video source is loaded (even paused), confirm before interrupting it.
Cancel leaves playback intact. This does not bypass Safari's autoplay rules,
clear offline caches or change another client/recording. Online service-worker
shell requests remain network-first, so a reload can fetch the installed update.

The deck has Controls, Recordings, Guide and Videos tabs. Portrait starts on
Recordings: this is a content browser rather than a miniature STV remote.
Landscape retains the normal STV, while Controls remains optional in portrait.
Recordings default to series folders; Videos to actual import-relative folders.
Both offer Series, Folders, Category and All items, item counts and tappable
breadcrumbs. Grouping is local and never renames/moves media or changes SageMC
preferences. Missing relative metadata falls back to root items. Only public
GetMediaFileRelativePath is exposed; absolute server paths/traversal are omitted.
Results currently retain the existing500-item bound with an explicit warning
and search, so folder counts describe loaded matching items, not an unseen
larger library. No arbitrary filesystem browsing is provided.

Guide is a channel/time grid with two-axis touch/keyboard scrolling, pinned
channel labels/logos and time headers, duration-proportional programs, Earlier/
Now/Later four-hour windows and search. Its data/lineup/logos come from the
connected server's existing SageTV guide, not a new feed or the wrong server.
Only same-origin SageTV logo URLs load; missing logos retain channel text.
Channel logos are served by the authenticated, station-ID-only public SageTV
logo adapter (`api/channelLogo?stationId=...`); there is no arbitrary URL/file
proxy. PNG/JPEG/GIF signatures and a1MiB bound are enforced, with text fallback.
Selecting a program shows a readable details card within the remaining deck,
not below the phone screen. Its sticky Back to guide button and Escape restore
the selection; short displays scroll the card. Explicit actions are:
Play for live/recorded items, Record for future programs, and Info. Future
Record is the existing public guide action, never an automatic consequence of
selection. A public asynchronous Record receipt means accepted, not yet
scheduled: read-only status confirmation distinguishes the two. It is not
replayed after an unknown response. Recordings/videos also
offer Info alongside Play. Info opens exact selected content in the native STV
without Watch: qualified SageMC Program Info or stock SageTV7 details menus via
public widget/context APIs only. Unknown/custom/ambiguous menus or an open STV
dialog refuse safely; no menu/widget edits, expressions or Core replacement.

Controls reuse the
same Vibe buttons/listeners in a non-scrolling six-column44px grid. The other
tabs have search, Refresh and their own scroll window. There are no background
guide polls. Library lists are capped at500; search narrows larger libraries.
The Guide retains up to6000airings per bounded window and warns at the cap. Normal
landscape/desktop keep the existing overlay, not duplicate controls.

Play explicitly targets the currently connected browser MiniClient. The normal
MiniClient command protocol has no media-ID/airing-ID Watch command: a pure
browser shortcut could only navigate/scrape unknown STV menus, not safely select
an arbitrary content item. Therefore the owning Web Client plugin supplies one
bounded `watchContent` action using supported `sage.SageTV.api/apiUI` operations.
It requires exactly one valid local UI identity and one content ID, refuses
missing/ambiguous/foreign contexts and future airings, and calls Watch once.
There is no MCP/Client Extension dependency, Core patch, arbitrary file-path
input, standalone video player, position reset, watched-state edit or retry.
The browser additionally waits for public exact-content/loaded/modal truth,
then requests one ordinary TV transition only from known preview bounds.
Already-fullscreen stays unchanged. Native input, another intent, Exit or
connection replacement cancels the wait; an uncertain transition is not retried.
Options dialogs/unknown state retain Controls rather than being dismissed.
Public Watch may return an opaque asynchronous task receipt rather than a
Boolean. Accept dispatch without inspecting private task classes or polling
under the request lock; explicit false/error responses still fail without
replay. Watch acknowledgement is not a claim of presented pictures. SageTV may show
its normal dialogs. An explicit live Play uses SageTV's normal live tuning and
temporary recording; it does not separately schedule a recording through the
Guide servlet. Future Guide items without recorded media have Play disabled.

Existing authenticated recording/guide GET endpoints are reused. `kind=videos`
selects non-TV video imports/DVD/Blu-ray rather than music or pictures; default
recording behavior is unchanged. All labels/descriptions use textContent.
Tab changes abort/retire old reads and cancel held remote input. Stale list
responses cannot populate another tab. A single pending Play disables all Play
buttons, preserves an uncertain outcome and never automatically replays it.

Affected qualification: production-DOM portrait/list/error/ownership/rotation
fixtures in Chromium and host WebKit; existing keyboard/settings/long-press,
landscape/safe-area, retained-surface rotation and PWA suites; Java exact-Watch
guards, stock compilation/package/served bytes and actual stock playback.
Browser emulation is not a physical iPhone/touch/audio acceptance claim.
Initial portrait normal manager3.3.0.20261118.002951 uses unchanged stock232. Actual
WebKit/SageMC and Chromium/SageTV7 each pass12rows including real107logo
decodes, correct selected Info menus, exact fullscreen Play/new video frames,
rotation and preserved profiles. See compact WEB-079/080 results. Future
recording side effects remain unqualified until an owned future-airing fixture
is available; production user programmes are not disposable test fixtures.
Physical040014Z portrait393x793 actual BLE folder/Guide/Info/Play passes;
user rotation040224Z852x393 restores native landscape. This does not imply
finger/scroll-inertia/acoustic/WAN acceptance. Later081playback-only updates
preserve these unchanged portrait assets; current installed build is in README.
