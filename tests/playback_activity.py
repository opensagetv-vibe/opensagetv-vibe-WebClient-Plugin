"""Read-only activity policy for non-disruptive public-HLS field consumers.

Playback is not a restart. Known co-tenants are supported; their resources
must not be attributed solely to the field consumer. Restart guards are separate.
"""
def observe_activity(value, require_isolation=False, require_other_client=False):
    keys = ('recordingCount', 'uiContextCount', 'connectedClientCount')
    if not isinstance(value, dict) or value.get('ok') is not True:
        raise RuntimeError('Playback activity is unknown')
    counts = {key: value.get(key) for key in keys}
    if any(type(count) is not int or count < 0 for count in counts.values()):
        raise RuntimeError('Playback activity counts are unknown')
    shared = any(counts.values())
    if require_isolation and shared:
        raise RuntimeError('Explicit isolated-resource gate requires no co-tenants')
    if require_other_client and not (counts['uiContextCount'] or counts['connectedClientCount']):
        raise RuntimeError('Concurrent-client gate needs an existing other client')
    return dict(counts, coTenancyObserved=shared,
                resourceScope='shared-server' if shared else 'server-container')


def observe_idle_phone_field(value, contexts, read_state, allow_idle_phone=False):
    """Permit one explicitly commissioned idle phone, never another player.

    This is a playback preflight, NOT restart-idle proof. No settings/commands
    are sent. Unknown/inconsistent counts or phone state refuse the field.
    """
    counts = observe_activity(value)
    if counts['recordingCount'] or counts['connectedClientCount']:
        raise RuntimeError('Recordings/native clients prevent isolated field')
    if not isinstance(contexts, list) or counts['uiContextCount'] != len(contexts):
        raise RuntimeError('UI activity is inconsistent')
    if not contexts:
        return dict(counts, idlePhoneObserved=False, safeToRestart=False)
    if not allow_idle_phone or contexts != ['123c8282e1ee']:
        raise RuntimeError('Only an explicitly allowed idle commissioned phone may coexist')
    state = read_state('123c8282e1ee')
    if (not isinstance(state, dict) or state.get('ok') is not True or
            state.get('context') != '123c8282e1ee' or
            state.get('fullyLoaded') is not False or state.get('loading') is not False):
        raise RuntimeError('Commissioned phone is active or unknown; preserve it')
    return dict(counts, idlePhoneObserved=True, safeToRestart=False)
