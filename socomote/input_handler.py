import logging
from threading import Thread
from typing import Iterable, Any

from getkey import getkey, keys

from socomote.action import *

from queue import Queue
logger = logging.getLogger(__name__)

class InputHandler:

    ENTER: str
    MODE: str

    def main(self) -> Iterable[Action]:
        buffer = ''
        for char in self.input():
            # char = self.get_char()
            logger.debug(f"Received {repr(char)}")
            input = None
            if char.isdigit():
                buffer += char
                logger.debug(f"Added {repr(char)} to buffer. Buffer is now {repr(buffer)}.")
            elif char in (self.ENTER, self.MODE):
                is_enter = char == self.ENTER
                logger.debug(f"Received {'ENTER' if is_enter else 'MODE'}. Handling buffer.")
                try:
                    i = int(buffer)
                    if i == 0:
                        input = None
                        logger.error("Entered 0 but stations/groups are 1-indexed.")
                    else:
                        if is_enter:
                            # translate to zero indexing for station data structures. (probably should change this)
                            input = i - 1
                        else:
                            input = f"{i}m" # pretty hack way to indicate MODE was pressed..
                except ValueError:
                    pass
                finally:
                    buffer = ''
            else:
                if buffer != '':
                    logger.info("Non-enter or int received while buffer is non-empty, clearing buffer.")
                    buffer = ''
                input = char
            if input is not None:
                try:
                    logger.info(f"Handling input {repr(input)}.")
                    yield self.handle(input)
                except:
                    pass
            else:
                logger.info("No valid input. Continuing.")

    def input(self):
        while True:
            yield self.get_char()

    def get_char(self) -> str:
        raise NotImplementedError

    def handle(self, input: Any) -> Action:
        raise NotImplementedError


class KeyboardInputHandler(InputHandler):

    ENTER = keys.ENTER
    MODE = 'm'

    def get_char(self) -> str:
        return getkey()

    def handle(self, inp: Any) -> Action:
        if inp == 'p':
            return PlayPause()
        elif inp == keys.UP:
            return VolUp()
        elif inp == keys.DOWN:
            return VolDown()
        elif inp == keys.LEFT:
            return Previous()
        elif inp == keys.RIGHT:
            return Next()
        elif inp == 's':
            return ShuffleStation()
        elif isinstance(inp, int):
            return SelectStation(inp)
        elif inp == 'h':
            return Speak()
        elif inp == 'q':
            return Query()
        elif isinstance(inp, str) and inp.endswith('m'):
            group_ix = int(inp[:-1])
            return SelectGroup(group_ix)
        else:
            logger.error(f"Unrecognised input {repr(input)}")
