# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyLab/SessionComponent.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from _Arturia.SessionComponent import SessionComponent as SessionComponentBase

class SessionComponent(SessionComponentBase):

    def set_selected_scene_launch_button(self, button):
        self.selected_scene().set_launch_button(button)
