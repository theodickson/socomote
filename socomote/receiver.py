import logging
import random
import time
from queue import Queue
from threading import Thread
from typing import Optional

from soco import SoCo

from socomote.action import *
from socomote.input_handler import InputHandler
from socomote.settings import GROUP_CONFIG, ZONES
from socomote.station import Station, Stations, is_station_uri
from socomote.tts_server import TTSServer

logger = logging.getLogger(__name__)

class Receiver:

    def __init__(self, controller: SoCo):
        self._controller: SoCo = controller
        self._handler = InputHandler()
        self._stations = Stations()  # todo - stations need refreshing
        self._tts_server = TTSServer()
        self._action_queue = Queue()
        self._action_thread = Thread(target=self._process_actions, daemon=True)

    def __enter__(self):
        self._tts_server.__enter__()
        self._action_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tts_server.__exit__(exc_type, exc_val, exc_tb)

    def start(self):
        for action in self._handler.actions():
            if self._action_queue.qsize() <= 3:
                self._action_queue.put(action)
            else:
                logger.info(f"Could not add {action} to action queue, queue full. Discarding action.")

    def _process_actions(self):
        while True:
            action = self._action_queue.get()
            logger.info(f"Performing action {action}")
            try:
                if isinstance(action, PlayPause):
                    self.play_pause()
                elif isinstance(action, VolUp):
                    self._controller.volume += 3
                elif isinstance(action, VolDown):
                    self._controller.volume -= 3
                elif isinstance(action, Next):
                    self.prev_next(is_next=True)
                elif isinstance(action, Previous):
                    self.prev_next(is_next=False)
                elif isinstance(action, SelectStation):
                    self.play_station_by_index(action.ix)
                elif isinstance(action, ShuffleStation):
                    station = random.choice(self._stations)
                    logger.info(f"Playing random station: {station}")
                    self.play_station(station)
                elif isinstance(action, Query):
                    self.query_station()
                elif isinstance(action, SelectGroup):
                    self.to_group(action.ix)
            except BaseException as e:
                logging.error(f"Unhandled exception: {e}")

    def _is_playing(self):
        # todo - get rid
        curr_info = self._controller.get_current_track_info()
        position = curr_info['position']
        logger.debug(f"Current position is {repr(position)}")
        if position is None or position == '' or position == '0:00:00':
            logger.debug(f"Currently paused.")
            return False
        else:
            logger.debug(f"Currently playing.")
            return True

    def _take_control(self):
        if self._controller.group.coordinator != self._controller:
            slaves = [s for s in self._controller.group if s != self._controller]
            logger.info(
                f"Controller {self._controller.player_name} is not the master, "
                f"taking control of: {[s.player_name for s in slaves]}"
            )
            for s in slaves:
                s.unjoin()
            for s in slaves:
                s.join(self._controller)

    def _play_uri(self, uri="", meta="", title="", start=True, force_radio=False):
        self._take_control()
        self._controller.play_uri(uri=uri, meta=meta, title=title, start=start, force_radio=force_radio)

    def _speak(self, text):
        uri = self._tts_server.get_uri(text)
        self._play_uri(uri=uri, title=text)

    def play_station(self, station: Station):
        logger.info(f"Playing station {station}")
        self._speak(station.title)
        time.sleep(2)  # todo
        start = time.time()
        self._play_uri(uri=station.uri, title=station.title)
        end = time.time()
        duration = end - start
        logger.debug(f"Took {duration} to play URI")

    def play_station_by_index(self, ix: int):
        station = self._stations[ix]
        self.play_station(station)

    def play_pause(self):
        self._take_control()
        if not self._is_playing():
            logger.debug(f"Sending play command")
            self._controller.play()
        else:
            logger.debug(f"Sending pause command")
            self._controller.pause()

    def prev_next(self, is_next: bool):
        station = self.current_station()
        if station is not None:
            logger.info(f"Current station is {station}.")
            index = self._stations.get_index(station)
            if index is not None:
                logger.info(f"Current station index is {index}.")
                if is_next:
                    to_play = self._stations.next_station(index)
                else:
                    to_play = self._stations.prev_station(index)
                self.play_station(to_play)
                return
            else:
                logger.error(f"No index for current station. It must not be a sonos favourite.")
        else:
            logger.info(f"Not currently playing a radio station, doing next/prev command.")
            self._take_control()
            if is_next:
                self._controller.next()
            else:
                self._controller.previous()

    def current_station(self) -> Optional[Station]:
        info = self._controller.get_current_media_info()
        if is_station_uri(info['uri']):
            return Station(title=info['channel'], uri=info['uri'])
        else:
            logger.info(f"Currently playing from channel {info['channel']}, uri {info['uri']} not a station.")

    def query_station(self):
        current = self.current_station()
        if current is not None:
            self.play_station(current)

    def to_group(self, i: int):
        self._take_control()
        current_slaves = sorted([
            s.player_name for s in self._controller.group if s != self._controller
        ])
        target_slaves = sorted(GROUP_CONFIG[self._controller.player_name][i])
        if target_slaves != current_slaves:
            logger.info(f"Grouping with target slaves {target_slaves}. (Current slaves are: {current_slaves}")
            released_slaves = set(current_slaves) - set(target_slaves)
            new_slaves = set(target_slaves) - set(current_slaves)
            for slave in released_slaves:
                ZONES[slave].unjoin()
            for slave in new_slaves:
                ZONES[slave].join(self._controller)
        else:
            logger.info(f"Target slaves {target_slaves} are equivalent to the existing slaves.")
