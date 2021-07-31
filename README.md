Socomote
========

Socomote is an application for remote control of a Sonos system,
based on [SoCo](https://soco.readthedocs.io/en/latest/).

I wrote this because as great as Sonos is, you need to use a phone or computer to control it. Sometimes when I'm
around the house I just want to play the radio without having to use my phone and select from near-infinite options.

Socomote + raspbery pi + USB IR receiver + remote control works for this perfectly

Features:
1. Basic control when any media is playing - play/pause, skip, control volume. 
2. Toggle grouping of speakers
3. Play any radio stations saved to your Sonos Favourites.
4. Station names are announced using [FreeTTS](https://freetts.com/), so you know what you're listening to.
5. Extensible with custom commands and other plugins.

Known issues:
1. SoCo doesn't work with most streaming services due to auth issues, hence the limitation to radio stations.
Other media types do work, e.g. local files, but I haven't extended it to work with them.
2. Can only play from Sonos Favourites, and these are always ordered alphabetically.



Recommended hardware
-----------------

Socomote works cross-platform, and on any input device that can mimic a keyboard. My setup is as
follows:
 - Raspberry Pi Zero W
   - Plus [this](https://thepihut.com/products/usb-to-microusb-otg-converter-shim) USB -> micro USB converter
 - [FLIRC USB](https://flirc.tv/more/flirc-usb)
 - [This](https://thepihut.com/products/mini-remote-control) cheap generic remote control

FLIRC USB is just a USB IR receiver that you can pair with any remote control and easily
map all of its keys to standard keystrokes using a simple GUI. As far as socomote is concerned,
it's just a keyboard.


Setup
-----
1. If using FLIRC or similar, map the keys on your remote according to the command table below.
2. Connect your device to the same network as your Sonos system.
3. `pip3 install socomote`
4. `python -m socomote` - The first run, if it detects no socomote config, will copy the example config
   to `~/socomote/config.yaml`
4. Edit the config to describe your system. The example file is fully documented, so just open it up and edit away.

If installing on a raspberry-pi like device that will be used solely for socomote, you may
want to configure it so that the application starts automatically on startup.

I've done this by setting the raspberry pi to boot to the CLI, and adding `python -m socomote` to the
end of my `~/.bashrc`.

Additionally I have aliased `000` to `sudo shutdown now` so I can shut down the raspberry pi with
my remote.


Usage
-----

1. `python3 -m socomote`
2.  Start entering commands!


| Key         | Action            | Help                                                                                                                              |
|-------------|-------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| UP          | Increase volume   | Default increment is 3, out of a scale of 0-100. This can be configured globally or per-zone in the config.yaml.                  |
| DOWN        | Decrease volume   |                                                                                                                                   |
| LEFT        | Previous          | If playing a Sonos Favourite radio station, go to the previous station in the list. Otherwise, attempt to skip to previous track. |
| RIGHT       | Next              |                                                                                                                                   |
| p           | Toggle play/pause |                                                                                                                                   |
| s           | Shuffle station   | Play a random station from your favourites                                                                                        |
| m           | Toggle mute       |                                                                                                                                   |
| a           | Announce station  | Re-announce the name of the currently playing station, if a radio station                                                         |
| {n} + ENTER | Play station      | Play station number n                                                                                                             |
| {n} + g     | Select group      | Select zone group n for the current master zone. 1 is reserved for the group just containing the master zone, 9 is reserved all zones.                                |
| {n} + z     | Set master zone   | Set the main speaker/zone your socomote instance is controlling                                                                   |
| 000 + ENTER | Exit              |                                                                                                                                   |


### Radio stations
This list of radio stations is generated automatically by taking all radio stations saved to your Sonos favourites. This
seemed like the easiest way to have a maintainable list of presets. The downside is that you can't order your favourites,
they are always alphabetical. Hence the station numbers are in alphabetical order, and so will change as you edit your
favourites.

I may revisit this and try to add a configurable presets system.


Customisation
-------------
TODO


Known issues
------------
- Can't play non-radio stations saved to your presets, even though SoCo supports lots of other media types [besides most major
streaming services](https://github.com/SoCo/SoCo/issues/557), e.g. local files. This is likely a pretty simple addition, 
  but I don't use anything else besides affected streaming services and radio, so haven't tried.
  The one difficulty here is that currently socomote doesn't differentiate
  between changing station and skipping track, both are achieved with LEFT/RIGHT. (If a favourite station is playing,
  it will change station, otherwise it will try to skip track, which does work if something is already streaming.)
  