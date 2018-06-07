# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/iRig_Keys_IO/skin.py
# Compiled at: 2018-05-12 02:03:19
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface import Skin
from ableton.v2.control_surface.elements import Color

class Colors:

    class DefaultButton:
        On = Color(0)
        Off = Color(0)
        Disabled = Color(0)

    class Transport:
        PlayOn = Color(0)
        PlayOff = Color(0)

    class Recording:
        On = Color(0)
        Off = Color(0)


skin = Skin(Colors)
