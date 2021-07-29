import logging
from logging.handlers import RotatingFileHandler
import sys
from argparse import ArgumentParser

from socomote.receiver import Receiver
from socomote.settings import ZONES, CONFIG, SOCOMOTE_HOME

parser = ArgumentParser()
parser.add_argument("--zone", "-z", help="Sonos zone to control (defaults to 'zone' in config.json).")
parser.add_argument("--debug", "-d", action="store_true", help="Run in DEBUG mode.")
parser.add_argument("--console-log", "-cl", action="store_true", help="Log to console, not file.")


def main(receiver: Receiver):
    with receiver as r:
        r.start()
    return 0

if __name__ == '__main__':
    args = parser.parse_args()
    logging_level = logging.DEBUG if args.debug else logging.INFO

    logging.getLogger('soco').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('getkey').setLevel(logging.ERROR)

    if args.console_log:
        handler = logging.StreamHandler(sys.stdout)
    else:
        filename = str(SOCOMOTE_HOME / "main.log")
        handler = RotatingFileHandler(filename=filename, maxBytes=10*1024*1024)

    logging.basicConfig(
        level=logging_level, format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s", handlers=[handler]
    )
    logger = logging.getLogger(__name__)
    zone_name = args.zone if args.zone is not None else CONFIG["zone"]
    logger.info(f"Starting socomote receiver for zone '{zone_name}'...")
    controller = ZONES[zone_name]
    receiver = Receiver(controller)

    sys.exit(main(receiver))
