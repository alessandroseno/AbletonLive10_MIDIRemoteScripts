# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyLab_Essential/mixer.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip_longest
from ableton.v2.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v2.control_surface.components.mixer import simple_track_assigner
from .channel_strip import ChannelStripComponent

class MixerComponent(MixerComponentBase):

    def _create_strip(self):
        return ChannelStripComponent()
