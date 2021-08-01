from dataclasses import dataclass

from socomote.core import KeyCommand, Receiver


@dataclass
class ToggleStatusLight(KeyCommand):
    """
    Toggle the status light on the master zone speaker(s).
    """
    key = 'l'

    def execute(self, receiver: Receiver):
        receiver.master_zone.status_light = not receiver.master_zone.status_light