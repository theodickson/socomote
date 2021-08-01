import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Iterable, Optional, ClassVar

from soco import SoCo
from yaml import dump
from getkey import getkey

from socomote.config import ZONES, CONFIG, SOCOMOTE_MASTER_ZONE_FILE, EXIT_CODE
from socomote.keys import Keys
from socomote.station import Station, Stations, is_station_uri
from socomote.tts_server import TTSServer

logger = logging.getLogger(__name__)

class Receiver:

    def __init__(self, master_zone: SoCo):
        self.master_zone: SoCo = master_zone
        self.stations = Stations()
        self._tts_server = TTSServer()
        self._executor = CommandExecutor(self)

    def __enter__(self):
        self._exit = False
        self._tts_server.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tts_server.__exit__(exc_type, exc_val, exc_tb)

    def run(self):
        self.speak("Socomote hello!")
        self._executor.run()
        self.speak("Socomote goodbye.")

    def take_control(self):
        """
        Set the master zone to be the coordinator of the group it's in.
        This is necessary before various actions as non-coordinator zones cannot do various thing such as playing URIs.
        """
        if self.master_zone.group.coordinator != self.master_zone:
            slaves = [s for s in self.master_zone.group if s != self.master_zone]
            logger.info(
                f"Controller {self.master_zone.player_name} is not the master, "
                f"taking control of: {[s.player_name for s in slaves]}"
            )
            for s in slaves:
                s.unjoin()
            for s in slaves:
                s.join(self.master_zone)

    def play_uri(self, uri="", meta="", title="", start=True, force_radio=False, take_control=True):
        """Wrapper for _master_zone.play_uri which first takes control to ensure the play_uri call succeeds"""
        if take_control:
            self.take_control()
        self.master_zone.play_uri(uri=uri, meta=meta, title=title, start=start, force_radio=force_radio)

    def speak(self, text: str, sleep_seconds: int = 2):
        """
        Convert the given text to speech and play it. See `tts_server` for details.
        :param text: Text to speak
        :param sleep_seconds: How long to sleep after sending the text (should be at least as long as the text will take)
        """
        uri = self._tts_server.get_uri(text)
        self.play_uri(uri=uri, title=text)
        time.sleep(sleep_seconds)

    def current_station(self) -> Optional[Station]:
        """
        Return the currently playing station, if a radio station, else None
        """
        info = self.master_zone.get_current_media_info()
        if is_station_uri(info['uri']):
            return Station(title=info['channel'], uri=info['uri'])
        else:
            logger.info(f"Currently playing media: {info['channel']}, uri {info['uri']} not a station.")


    def play_station(self, station: Station, announce_title=True):
        """
        Play the given station after speaking its title.
        """
        logger.info(f"Playing station {station}")
        if announce_title:
            self.speak(station.title)
        self.play_uri(uri=station.uri, title=station.title)

    def vol_change(self, up: bool):
        increment = CONFIG['Zones'][self.master_zone.player_name].get('VolumeIncrement')
        if increment is None:
            increment = CONFIG.get('VolumeIncrement', 3)
        logger.debug(f"Volume change: Volume is currently {self.master_zone.volume}")
        if up:
            logger.debug(f"Increasing volume by {increment}")
            self.master_zone.volume += increment
        else:
            logger.debug(f"Decreasing volume by {increment}")
            self.master_zone.volume -= increment
        logger.debug(f"Volume is now {self.master_zone.volume}")

    def prev_next(self, is_next: bool):
        station = self.current_station()
        if station is not None:
            logger.info(f"Current station is {station}.")
            to_play = self.stations.prev_next(station, is_next=is_next)
            if to_play is not None:
                self.play_station(to_play)
        else:
            logger.info(f"Not currently playing a radio station, doing next/prev command.")
            self.take_control()
            if is_next:
                self.master_zone.next()
            else:
                self.master_zone.previous()


class Command(ABC):
    _key_commands = {}
    _code_commands = {}
    _special_code_commands = {}

    @abstractmethod
    def execute(self, receiver: Receiver):
        ...

    @classmethod
    def from_input(cls, key: str, code: Optional[str] = None) -> Optional['Command']:
        if code is not None and (key, code) in cls._special_code_commands:
            return cls._special_code_commands[(key, code)]()
        elif code is not None and key in cls._code_commands:
            return cls._code_commands[key](code)
        elif code is None and key in cls._key_commands:
            return cls._key_commands[key]()
        logger.error(f"Unable to construct command from key='{key}', code='{code}'")


class KeyCommand(Command):
    key: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        if cls.key in cls._key_commands:
            raise Exception(f"KeyCommand {cls._key_commands[cls.key]} already registered for key {cls.key}")
        cls._key_commands[cls.key] = cls


@dataclass
class CodeCommand(Command):
    terminal: ClassVar[str]
    code: str

    @property
    def int_code(self) -> int:
        return int(self.code)

    def __init_subclass__(cls, **kwargs):
        if cls.terminal in cls._code_commands:
            raise Exception(
                f"CodeCommand {cls._code_commands[cls.terminal]} already registered for terminal {cls.terminal}"
            )
        cls._code_commands[cls.terminal] = cls


class SpecialCodeCommand(Command):
    terminal: ClassVar[str]
    code: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        if (cls.terminal, cls.code) in cls._special_code_commands:
            raise Exception(
                f"SpecialCodeCommand {cls._special_code_commands[(cls.terminal, cls.code)]} "
                f"already registered for terminal={cls.terminal}, code={cls.code}"
            )
        cls._special_code_commands[(cls.terminal, cls.code)] = cls


@dataclass
class PlayPause(KeyCommand):
    key = Keys.PLAY_PAUSE

    def execute(self, receiver: Receiver):
        receiver.take_control()
        curr_info = receiver.master_zone.get_current_track_info()
        position = curr_info['position']
        logger.debug(f"Current position is {repr(position)}")
        if position is None or position == '' or position == '0:00:00':
            logger.debug(f"Currently paused, playing")
            receiver.master_zone.play()
        else:
            logger.debug(f"Currently playing, pausing")
            receiver.master_zone.pause()


@dataclass
class VolUp(KeyCommand):
    key = Keys.UP

    def execute(self, receiver: Receiver):
        receiver.vol_change(up=True)


@dataclass
class VolDown(KeyCommand):
    key = Keys.DOWN

    def execute(self, receiver: Receiver):
        receiver.vol_change(up=False)


@dataclass
class ToggleMute(KeyCommand):
    key = Keys.MUTE

    def execute(self, receiver: Receiver):
        receiver.master_zone.mute = not receiver.master_zone.mute


@dataclass
class SelectStation(CodeCommand):
    terminal = Keys.ENTER

    def execute(self, receiver: Receiver):
        station = receiver.stations[self.int_code]
        receiver.play_station(station)


@dataclass
class ShuffleStation(KeyCommand):
    key = Keys.SHUFFLE

    def execute(self, receiver: Receiver):
        station = random.choice(receiver.stations)
        logger.info(f"Playing random station: {station}")
        receiver.play_station(station)


@dataclass
class Next(KeyCommand):
    key = Keys.RIGHT

    def execute(self, receiver: Receiver):
        receiver.prev_next(is_next=True)


@dataclass
class Previous(KeyCommand):
    key = Keys.LEFT

    def execute(self, receiver: Receiver):
        receiver.prev_next(is_next=False)


@dataclass
class Announce(KeyCommand):
    key = Keys.ANNOUNCE

    def execute(self, receiver: Receiver):
        # If currently playing a station, re-play it, as this will announce the title
        # then immediately restart.
        # Can't easily implement for other media types as e.g. soco can't play streaming service URIs
        current = receiver.current_station()
        if current is not None:
            receiver.play_station(current)


@dataclass
class SelectGroup(CodeCommand):
    terminal = Keys.GROUP

    def execute(self, receiver: Receiver):
        receiver.take_control()
        current_slaves = {s.player_name for s in receiver.master_zone.group if s != receiver.master_zone}
        if self.int_code == 1:
            # reserved for the group just containing the master zone
            target_slaves = set()
        elif self.int_code == 9:
            # reserved for all available zones
            target_slaves = {name for name in ZONES if name != receiver.master_zone.player_name}
        else:
            target_slaves = set(CONFIG['Zones'][receiver.master_zone.player_name]['Groups'][self.int_code])
        if target_slaves != current_slaves:
            logger.info(f"Grouping with target slaves {target_slaves}. (Current slaves are: {current_slaves}")
            released_slaves = current_slaves - target_slaves
            new_slaves = target_slaves - current_slaves
            for slave in released_slaves:
                ZONES[slave].unjoin()
            for slave in new_slaves:
                ZONES[slave].join(receiver.master_zone)
        else:
            logger.info(f"Target slaves {target_slaves} are equivalent to the existing slaves.")


@dataclass
class SetMaster(CodeCommand):
    terminal = Keys.ZONE

    def execute(self, receiver: Receiver):
        # Retrieve the new controller
        controller: SoCo
        for name, zone in CONFIG['Zones'].items():
            if zone['Index'] == self.int_code:
                controller = ZONES[name]
                break
        else:
            raise Exception(f"No zone with index {self.int_code}")

        if controller.player_name != receiver.master_zone.player_name:
            logger.info(f"Setting master zone to {controller.player_name}")
            # Edit the master zone config/file
            MASTER_ZONE = self.int_code
            with SOCOMOTE_MASTER_ZONE_FILE.open('w') as f:
                f.write(dump({"MasterZone": MASTER_ZONE}))
            receiver.master_zone = controller
            receiver.take_control()
            receiver.speak("Socomote hello!")


@dataclass
class Exit(SpecialCodeCommand):
    terminal = Keys.ENTER
    code = EXIT_CODE

    def execute(self, receiver: Receiver):
        # Don't have to set the flag here, see CommandExecutor.run
        logger.info("Exiting.")


class CommandExecutor:

    def __init__(self, receiver: Receiver):
        self.receiver = receiver
        self._exit = False
        self._queue: Queue[Command] = Queue()
        self._execution_thread = Thread(target=self._execute_commands)

    def run(self):
        self._execution_thread.start()
        for command in self.commands():
            if self._queue.qsize() > 3:
                logger.info(f"Could not add {command} to queue, queue full. Discarding.")
                continue
            if isinstance(command, Exit):
                # Set the flag in the main thread so we don't hit a subsequent call to getkey
                self._exit = True
            self._queue.put(command)
        logger.debug("Waiting for execution thread to exit.")
        self._execution_thread.join()
        logger.debug("Done.")

    def commands(self) -> Iterable[Command]:
        digit_buffer = ''
        while not self._exit:
            logger.debug("Getting key")
            key = getkey()
            logger.debug(f"Received {repr(key)}")
            cmd = None
            if key.isdigit():
                digit_buffer += key
                logger.debug(f"Added {repr(key)} to buffer. Buffer is now {repr(digit_buffer)}.")
            elif key in Keys.TERMINALS and digit_buffer != '':
                logger.debug(f"Received terminal key {key}. Handling buffer.")
                cmd = Command.from_input(key, digit_buffer)
                digit_buffer = ''
            elif digit_buffer != '':
                logger.debug("Non-digit or terminal key received while buffer is non-empty, clearing buffer and ignoring key.")
                digit_buffer = ''
            else:
                # Note that terminal keys will be yielded as key commands if digit buffer is empty
                # This is intentional as terminal keys may be re-used as key commands (e.g. SETUP as QUERY by default)
                cmd = Command.from_input(key)
            if cmd is not None:
                yield cmd

    def _execute_commands(self):
        while not self._exit:
            command = self._queue.get()
            logger.info(f"Executing command {command}")
            try:
                command.execute(self.receiver)
            except BaseException as e:
                logging.error(f"Unhandled exception executing command {command}: {e}")
