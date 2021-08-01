import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict
from importlib import __import__

from yaml import safe_load as load, safe_dump as dump
import soco
from soco import SoCo


logger = logging.getLogger(__name__)

ZONES: Dict[str, SoCo] = {}
for zone in soco.discover():
    ZONES[zone.player_name] = zone


SOCOMOTE_HOME = Path(
    os.environ.get('SOCOMOTE_HOME', '~/socomote')
).expanduser()
SOCOMOTE_HOME.mkdir(parents=True, exist_ok=True)

LOG_FILE = SOCOMOTE_HOME / "main.log"

SOCOMOTE_CONFIG_FILE = SOCOMOTE_HOME / "config.yaml"
# Copy the example config if the file doesn't exist, and exit, probably needs to be edited before socomote can run.
if not SOCOMOTE_CONFIG_FILE.exists():
    example_config = Path(__file__).parent / "resources" / "example_config.yaml"
    shutil.copy(example_config, SOCOMOTE_CONFIG_FILE)
    print(f"No socomote config found. Example config copied to {str(SOCOMOTE_CONFIG_FILE)}.")
    print("Please edit before re-running.")
    sys.exit(1)

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

EXIT_CODE = CONFIG.get('Codes', {}).get('EXIT', '000')

PLUGINS = SOCOMOTE_HOME / "plugins.py"
sys.path.append(str(SOCOMOTE_HOME))

if not PLUGINS.exists():
    example_plugins = Path(__file__).parent / "resources" / "example_plugins.yaml"
    shutil.copy(example_plugins, PLUGINS)

# use the __import__ function to not annoy the IDE
__import__("plugins")