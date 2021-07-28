import logging
from typing import Iterable, Any

from getkey import getkey, keys

from socomote.action import *

logger = logging.getLogger(__name__)

class InputHandler:

    def actions(self) -> Iterable[Action]:
        buffer = ''
        while True:
            char = getkey()
            logger.debug(f"Received {repr(char)}")
            input = None
            if char.isdigit():
                buffer += char
                logger.debug(f"Added {repr(char)} to buffer. Buffer is now {repr(buffer)}.")
            elif char in (keys.ENTER, 'm'):
                is_enter = char == keys.ENTER
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
                            input = f"{i}m" # pretty hacky way to indicate MODE was pressed..
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
                    yield self.handle_input(input)
                except:
                    pass
            else:
                logger.info("No valid input. Continuing.")

    def handle_input(self, inp: Any) -> Action:
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
        elif inp == 'q':
            return Query()
        elif isinstance(inp, str) and inp.endswith('m'):
            group_ix = inp[:-1]
            return SelectGroup(group_ix)
        else:
            logger.error(f"Unrecognised input {repr(input)}")
