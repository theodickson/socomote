import logging
from typing import Iterable

from getkey import getkey, keys

from socomote.action import *

logger = logging.getLogger(__name__)


class InputHandler:

    terminal_chars = {
        keys.ENTER,
        "m",
        "s",
    }

    def __init__(self):
        self.exited = False

    def actions(self) -> Iterable[Action]:
        for inp in self.inputs():
            yield self.to_action(inp)

    def inputs(self) -> Iterable[str]:
        digit_buffer = ''
        while True:
            if self.exited:
                break
            logger.debug("Getting key")
            char = getkey()
            logger.debug(f"Received {repr(char)}")
            input = None
            if char.isdigit():
                digit_buffer += char
                logger.debug(f"Added {repr(char)} to buffer. Buffer is now {repr(digit_buffer)}.")
            elif char in self.terminal_chars:
                logger.debug(f"Received terminal char {char}. Handling buffer.")
                input = f"{digit_buffer}{char}"
                digit_buffer = ''
            else:
                if digit_buffer != '':
                    logger.info("Non-digit or terminal char received while buffer is non-empty, clearing buffer.")
                    digit_buffer = ''
                input = char
            if input is not None:
                try:
                    yield input
                except:
                    pass
            else:
                logger.info("No valid input. Continuing.")

    def to_action(self, inp: str) -> Action:
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
        elif inp == 'r':
            return ShuffleStation()
        elif inp == 's':
            return Query()
        elif inp[0].isdigit():
            if inp == '000m':
                return Exit()
            i = int(inp[:-1])
            if inp[-1] == keys.ENTER:
                return SelectStation(i)
            elif inp[-1] == 'm':
                return SelectGroup(i)
            elif inp[-1] == 's':
                return SetMaster(i)
        logger.error(f"Unrecognised input {repr(input)}")
