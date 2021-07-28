import os
from pathlib import Path
from typing import Dict

import soco
from soco import SoCo

from socomote.input_handler import KeyboardInputHandler

ZONES: Dict[str, SoCo] = {}
for zone in soco.discover():
    ZONES[zone.player_name] = zone

GROUP_CONFIG = {
    'Study': {
        1: [],
        2: ['Kitchen']
    },

    'Kitchen': {
        1: [],
        2: ['Living Room'],
        3: ['Living Room', 'Study']
    },

    'Living Room': {
        1: [],
        2: ['Kitchen'],
        3: ['Kitchen', 'Study']
    }
}


HANDLERS = {
    'KEYBOARD': KeyboardInputHandler()
}

MP3_LIB = Path(
    os.environ.get('SOCOMOTE_MP3_LIB', '/Users/theo/development/socomote/mp3s')
)
