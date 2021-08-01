from getkey import keys

from socomote.config import CONFIG


class Keys:

    KEY_MAP = CONFIG.get('KeyMap', {})

    ENTER = keys.ENTER
    UP = keys.UP
    DOWN = keys.DOWN
    LEFT = keys.LEFT
    RIGHT = keys.RIGHT
    PLAY_PAUSE = KEY_MAP.get("PLAY_PAUSE", "p")
    NEXT_TRACK = KEY_MAP.get("NEXT_TRACK", "]")
    PREV_TRACK = KEY_MAP.get("PREV_TRACK", "[")
    SHUFFLE = KEY_MAP.get("SHUFFLE", "s")
    ANNOUNCE = KEY_MAP.get("ANNOUNCE", "a")
    MUTE = KEY_MAP.get("MUTE", "m")
    GROUP = KEY_MAP.get("GROUP", "g")
    ZONE = KEY_MAP.get("ZONE", "z")

    TERMINALS = {ENTER, GROUP, ZONE}