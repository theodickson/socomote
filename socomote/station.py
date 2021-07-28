import logging
import time
from dataclasses import dataclass, field
from threading import Thread

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
        self._refresh_thread = Thread(target=self.refresh, daemon=True)
        self._refresh_thread.start()

    def refresh(self):
        def inner():
            self._stations = []
            for fav in MusicLibrary().get_sonos_favorites():
                uri = fav.get_uri()
                if is_station_uri(uri):
                    self._stations.append(Station(fav.title, uri))
            self._station_index = {station: i for i, station in enumerate(self._stations)}
            logger.info(f"Stations list initialised, there are {len(self)}")
        while True:
            inner()
            time.sleep(10)

    def __iter__(self):
        return iter(self._stations)

    def __len__(self):
        return len(self._stations)

    def __getitem__(self, item):
        return self._stations[item]

    def get_index(self, item):
        return self._station_index.get(item)

    def next_station(self, ix):
        if 0 <= ix < len(self) - 1:
            return self[ix + 1]
        elif ix == len(self) - 1:
            return self[0]
        else:
            raise ValueError(f"Index {ix} is invalid, no next station can be found.")

    def prev_station(self, ix):
        if ix == 0:
            return self[len(self) - 1]
        elif 0 < ix < len(self):
            return self[ix - 1]
        else:
            raise ValueError(f"Index {ix} is invalid, no previous station can be found.")