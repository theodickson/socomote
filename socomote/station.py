import logging
import time
from dataclasses import dataclass, field
from threading import Thread
from typing import Optional

from soco.music_library import MusicLibrary

logger = logging.getLogger(__name__)

STATION_PREFIXES = [
    'x-sonosapi-stream:',
    'x-sonosapi-radio:',
    'x-rincon-mp3radio:',
    'hls-radio:'
]


def is_station_uri(uri):
    return any(uri.startswith(p) for p in STATION_PREFIXES)


@dataclass(frozen=True)
class Station:
    title: str
    uri: str = field(repr=False)


class Stations:

    def __init__(self):
        self._stations = []
        self._station_index = {}
        self.refresh()
        self._refresh_thread = Thread(target=self._refresh_loop, daemon=True)
        self._refresh_thread.start()

    def refresh(self):
        new_stations = []
        for fav in MusicLibrary().get_sonos_favorites():
            uri = fav.get_uri()
            if is_station_uri(uri):
                new_stations.append(Station(fav.title, uri))
        new_index = {station: i + 1 for i, station in enumerate(new_stations)}
        self._stations = new_stations
        self._station_index = new_index
        logger.info(f"Stations list initialised, there are {len(self)}")

    def _refresh_loop(self):
        while True:
            self.refresh()
            time.sleep(60)

    def __iter__(self):
        return iter(self._stations)

    def __len__(self):
        return len(self._stations)

    def __getitem__(self, item):
        # we 1-index the stations to correspond to button presses
        return self._stations[item - 1]

    def prev_next(self, station: Station, is_next: bool) -> Optional[Station]:
        index = self._station_index.get(station)
        if index is not None:
            logger.info(f"Current station index is {index}.")
            if is_next:
                new_index = self.next_index(index)
            else:
                new_index = self.prev_index(index)
            return self[new_index]
        logger.error(f"Current station is not a sonos favourite, cannot do next/prev station.")

    def next_index(self, ix: int) -> int:
        if 1 <= ix < len(self):
            return ix + 1
        elif ix == len(self):
            return 1
        else:
            raise ValueError(f"Index {ix} is invalid, no next station can be found.")

    def prev_index(self, ix: int) -> int:
        if ix == 1:
            return len(self)
        elif 1 < ix <= len(self):
            return ix - 1
        else:
            raise ValueError(f"Index {ix} is invalid, no previous station can be found.")