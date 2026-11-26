# Safari autoplay audit —2026-11-17

User reference: [Apple, Delivering Video Content for Safari](https://developer.apple.com/documentation/webkit/delivering-video-content-for-safari).
Reviewed alongside [WebKit iOS video policy](https://webkit.org/blog/6784/new-video-policies-for-ios/)
and [per-element guidance](https://webkit.org/blog/7734/auto-play-policy-changes-for-macos/).

Safari's documented gesture-free cases are muted media or media without an
audio track. Becoming audible without an accepted user gesture may pause it.
Inline playback uses playsinline; a rejected play Promise requires a visible
manual control. Website code cannot set native WKWebViewConfiguration policy
inside Safari/PWA. An iOS wrapper would be a separate project, not this
browser-only plugin. No such wrapper or platform-security change is made.

Current Web Client already provides inline native HLS on iPhone, a persistent
video element across source replacements, immediate play inside the existing
Play button handler, Promise rejection handling and a visible blocked-play
button. Mute is explicit user intent: do not silently mute to manufacture an
autoplay success, automatically unmute after a timer, remove required audio,
or restart FFmpeg merely because the browser requires interaction. An existing
Play/long-press control remains usable; no sound-autoplay guarantee is added.

Focused production-adapter policy tests cover allowed muted playback, blocked
audible playback without automatic muting/recovery loops, explicit gesture
retry, stale rejected Promise isolation and same-element reuse. Fake media
tests are policy regression evidence, not a physical Safari autoplay verdict.
Real iPhone trusted ESP32 BLE Play presses independently start native HLS with
actual advancing frames. They do not certify gesture-free sound or acoustic
sync. The test setup's remote Watch is not a phone user activation; its wait
at Play must not be attributed to encoder/first-segment startup time.

No runtime change was justified solely by the linked article. Retain the
manual Play fallback even for muted playback, because browser policy and
device state can still refuse it. This audit does not stop other field tasks.
