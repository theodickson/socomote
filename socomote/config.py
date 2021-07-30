import os
from pathlib import Path
from typing import Dict, Set

from yaml import safe_load as load, safe_dump as dump
import soco
from soco import SoCo

SOCOMOTE_HOME = Path(
    os.environ.get('SOCOMOTE_HOME', '~/socomote')
).expanduser()

SOCOMOTE_CONFIG_FILE = SOCOMOTE_HOME / "config.yaml"

MP3_LIB = SOCOMOTE_HOME / "mp3s"

LOG_FILE = SOCOMOTE_HOME / "main.log"

ZONES: Dict[str, SoCo] = {}
for zone in soco.discover():
    ZONES[zone.player_name] = zone

SOCOMOTE_CONFIG_FILE = SOCOMOTE_HOME / "config.yaml"
SOCOMOTE_MASTER_ZONE_FILE = SOCOMOTE_HOME / "master_zone.yaml"

with SOCOMOTE_CONFIG_FILE.open('r') as f:
    CONFIG = load(f.read())

with SOCOMOTE_MASTER_ZONE_FILE.open('r') as f:
    MASTER_ZONE = load(f.read())['MasterZone']
