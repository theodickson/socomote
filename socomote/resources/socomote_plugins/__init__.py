"""
Define any plugins here.
Plugins are so far intended to mainly be custom commands.
However as this module is imported before the receiver is initialised and started,
it can be used to monkeypatch any part of socomote as well
"""
from .custom_commands import *