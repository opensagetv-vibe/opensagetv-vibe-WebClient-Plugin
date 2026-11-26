"""Read-only clock checks for the canonical fixture's authored 20s chapter.

The DVD VM's read-ahead chapter is diagnostic, never a presented-frame oracle.
This does not alter clocks, media, playback or server state.
"""
import math


def fixture_replacement_command(sample):
    """Bound one source replacement within the canonical four-chapter title.

    Reader chapter selects a safe normal key, not a displayed-position oracle.
    Next from1; Previous from2..4 avoids walking into title EOF during repeats.
    The caller must separately prove replacement pictures and clock progress.
    """
    chapter=sample.get('dvdChapter')
    if sample.get('dvdMenu') is not False or sample.get('dvdTitle')!=1 or type(chapter) is not int or not 1<=chapter<=4:
        return None
    return 65 if chapter==1 else 66


def presentation_speed(before, after, wall_seconds):
    values=(before.get('frameTime'),after.get('frameTime'),wall_seconds)
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
        return None
    if wall_seconds < 4 or after.get('epoch') != before.get('epoch'):
        return None
    if after.get('frames',0) <= before.get('frames',0) or after.get('paused') is not False:
        return None
    return (after['frameTime']-before['frameTime'])/wall_seconds


def chapter_two_picture_clock(sample):
    if sample.get('nativeMenu') is not False or sample.get('title') != 1:
        return False
    presented = sample.get('lastPresented')
    raw = sample.get('rawMs')
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in (presented, raw)):
        return False
    # Generator MAIN_CHAPTERS=(0,20,40,60). Require pictures and a matching
    # title-relative Core clock inside chapter2, not merely a command ACK.
    return (sample.get('sourceChanged') is True and sample.get('frames', 0) >= 15
            and sample.get('ready', 0) >= 2 and sample.get('paused') is False
            and 0.5 <= presented < 18 and 18000 <= raw < 40000
            and abs(raw - (20000 + presented * 1000)) <= 2000)
