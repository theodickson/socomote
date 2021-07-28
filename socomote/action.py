"""
TODO:
- Random non-fav station
- Handle all errors, maybe some logging
- Handle station out of index
-
"""
from dataclasses import dataclass


@dataclass
class Action:
    pass

@dataclass
class PlayPause(Action):
    pass

@dataclass
class VolUp(Action):
    pass

@dataclass
class VolDown(Action):
    pass

@dataclass
class SelectStation(Action):
    ix: int

@dataclass
class ShuffleStation(Action):
    pass

@dataclass
class Next(Action):
    pass

@dataclass
class Previous(Action):
    pass

@dataclass
class Query(Action):
    pass

@dataclass
class SelectGroup(Action):
    ix: str