import logging
import sys
from argparse import ArgumentParser

from socomote.receiver import Receiver
from socomote.settings import ZONES, CONFIG

parser = ArgumentParser()
parser.add_argument("--zone", "-z", help="Sonos zone to control (defaults to 'zone' in config.json).")
parser.add_argument("--debug", "-d", action="store_true", help="Run in DEBUG mode.")

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

    logging.basicConfig(
        stream=sys.stdout, level=logging_level, format="[%(levelname)s] - %(name)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    zone_name = args.zone if args.zone is not None else CONFIG["zone"]
    logger.info(f"Starting socomote receiver for zone '{zone_name}'...")
    controller = ZONES[zone_name]
    receiver = Receiver(controller)

    sys.exit(main(receiver))
