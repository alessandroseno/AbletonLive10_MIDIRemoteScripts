# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyLab_Essential/skin_default.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface import Skin
from ableton.v2.control_surface.elements import Color
from .sysex_rgb_color import SysexRGBColor

class Colors:

    class DefaultButton:
        On = Color(127)
        Off = Color(0)
        Disabled = Color(0)

    class Transport:
        PlayOn = Color(127)
        PlayOff = Color(0)
        StopOn = Color(127)
        StopOff = Color(0)

    class Session:
        ClipStopped = SysexRGBColor((31, 31, 0))
        ClipStarted = SysexRGBColor((0, 31, 0))
        ClipRecording = SysexRGBColor((31, 0, 0))
        ClipTriggeredPlay = SysexRGBColor((0, 31, 0))
        ClipTriggeredRecord = SysexRGBColor((31, 0, 0))
        ClipEmpty = SysexRGBColor((0, 0, 0))
        StopClip = Color(0)
        StopClipTriggered = Color(0)
        StoppedClip = Color(0)


default_skin = Skin(Colors)
