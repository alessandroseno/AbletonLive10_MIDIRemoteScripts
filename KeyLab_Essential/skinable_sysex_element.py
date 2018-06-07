# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyLab_Essential/skinable_sysex_element.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface import Skin
from ableton.v2.control_surface.elements import SysexElement

class SkinableSysexElement(SysexElement):

    def __init__(self, skin=Skin(), *a, **k):
        super(SkinableSysexElement, self).__init__(*a, **k)
        self._skin = skin

    def set_light(self, value):
        color = self._skin[value]
        color.draw(self)
