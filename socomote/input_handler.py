import logging
from typing import Iterable

from getkey import getkey, keys

from socomote.action import *

logger = logging.getLogger(__name__)

class InputHandler:

    def __init__(self):
        self.exited = False

    def actions(self) -> Iterable[Action]:
        digit_buffer = ''
        while True:
            if self.exited:
                break
            char = getkey()
            logger.debug(f"Received {repr(char)}")
            input = None
            if char.isdigit():
                digit_buffer += char
                logger.debug(f"Added {repr(char)} to buffer. Buffer is now {repr(digit_buffer)}.")
            elif char in (keys.ENTER, 'm'):
                is_enter = char == keys.ENTER
                logger.debug(f"Received {'ENTER' if is_enter else 'MODE'}. Handling buffer.")
                if digit_buffer == '':
                    logger.debug(f"Empty buffer, nothing to do.")
                elif is_enter:
                    input = digit_buffer
                else:
                    input = digit_buffer + "m"
                digit_buffer = ''
            else:
                if digit_buffer != '':
                    logger.info("Non-enter or int received while buffer is non-empty, clearing buffer.")
                    digit_buffer = ''
                input = char
            if input is not None:
                try:
                    logger.info(f"Handling input {repr(input)}.")
                    yield self.handle_input(input)
                except:
                    pass
            else:
                logger.info("No valid input. Continuing.")

    def handle_input(self, inp: str) -> Action:
        if inp == keys.UP:
            return VolUp()
        elif inp == keys.DOWN:
            return VolDown()
        elif inp == keys.LEFT:
            return Previous()
        elif inp == keys.RIGHT:
            return Next()
        elif inp == 'p':
            return PlayPause()
        elif inp == 's':
            return ShuffleStation()
        elif inp == 'q':
            return Query()
        elif inp[0].isdigit():
            if inp == '000m':
                return Exit()
            elif inp[-1].isdigit():
                station_ix = int(inp)
                return SelectStation(station_ix)
            elif inp[-1] == 'm':
                return SelectGroup(inp[:-1])
        logger.error(f"Unrecognised input {repr(input)}")
