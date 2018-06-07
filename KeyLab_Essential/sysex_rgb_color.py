# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyLab_Essential/sysex_rgb_color.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface.elements import Color

class SysexRGBColor(Color):

    def __init__(self, midi_value=None, *a, **k):
        assert isinstance(midi_value, tuple) and len(midi_value) == 3
        super(SysexRGBColor, self).__init__(midi_value, *a, **k)
