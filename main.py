import logging
import os
import sys

from socomote.receiver import Receiver
from socomote.settings import ZONES, HANDLERS

if __name__ == '__main__':
    logging.getLogger('soco').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('getkey').setLevel(logging.ERROR)
    logging.basicConfig(
        stream=sys.stdout, level=logging.DEBUG, format="[%(levelname)s] - %(name)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    zone_name = os.environ.get('SOCOMOTE_ZONE', 'Living Room')
    handler_name = os.environ.get('SOCOMOTE_HANDLER', 'KEYBOARD')
    logger.info(f"Starting socomote receiver for zone '{zone_name}' with handler '{handler_name}'...")
    controller = ZONES[zone_name]
    handler = HANDLERS[handler_name]
    receiver = Receiver(controller, handler)

    with receiver as r:
        r.main()
