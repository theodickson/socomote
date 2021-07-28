import json
import os
from pathlib import Path
from typing import Dict

import soco
from soco import SoCo

ZONES: Dict[str, SoCo] = {}
for zone in soco.discover():
    ZONES[zone.player_name] = zone


SOCOMOTE_HOME = Path(
    os.environ.get('SOCOMOTE_HOME', '~/socomote')
).expanduser()


with (SOCOMOTE_HOME / "config.json").open() as f:
    CONFIG = json.load(f)

GROUP_CONFIG = CONFIG['group_config']

MP3_LIB = SOCOMOTE_HOME / "mp3s"
