import os
import shutil
from pathlib import Path
from typing import Dict

from yaml import safe_load as load, safe_dump as dump
import soco
from soco import SoCo

SOCOMOTE_HOME = Path(
    os.environ.get('SOCOMOTE_HOME', '~/socomote')
).expanduser()
SOCOMOTE_HOME.mkdir(parents=True, exist_ok=True)

LOG_FILE = SOCOMOTE_HOME / "main.log"

SOCOMOTE_CONFIG_FILE = SOCOMOTE_HOME / "config.yaml"
# Copy the example config if the file doesn't exist:
if not SOCOMOTE_CONFIG_FILE.exists():
    example_config = Path(__file__).parent / "resources" / "example_config.yaml"
    shutil.copy(example_config, SOCOMOTE_CONFIG_FILE)

SOCOMOTE_MASTER_ZONE_FILE = SOCOMOTE_HOME / "master_zone.yaml"
# Initialise the file with MasterZone=1 if it doesn't exist:
if not SOCOMOTE_MASTER_ZONE_FILE.exists():
    with SOCOMOTE_MASTER_ZONE_FILE.open('w') as f:
        f.write(dump({"MasterZone": 1}))

with SOCOMOTE_CONFIG_FILE.open('r') as f:
    CONFIG = load(f.read())

with SOCOMOTE_MASTER_ZONE_FILE.open('r') as f:
    MASTER_ZONE = load(f.read())['MasterZone']

MP3_LIB = SOCOMOTE_HOME / "mp3s"
MP3_LIB.mkdir(exist_ok=True)

ZONES: Dict[str, SoCo] = {}
for zone in soco.discover():
    ZONES[zone.player_name] = zone
