# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/ChannelTranslationSelector.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from .InputControlElement import InputControlElement
from .ModeSelectorComponent import ModeSelectorComponent

class ChannelTranslationSelector(ModeSelectorComponent):
    u""" Class switches modes by translating the given controls' message channel """

    def __init__(self, num_modes=0, *a, **k):
        super(ChannelTranslationSelector, self).__init__(*a, **k)
        self._controls_to_translate = None
        self._initial_num_modes = num_modes
        return

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._controls_to_translate = None
        return

    def set_controls_to_translate(self, controls):
        assert self._controls_to_translate == None
        assert controls != None
        assert isinstance(controls, tuple)
        for control in controls:
            if not isinstance(control, InputControlElement):
                raise AssertionError

        self._controls_to_translate = controls
        return

    def number_of_modes(self):
        result = self._initial_num_modes
        if result == 0 and self._modes_buttons != None:
            result = len(self._modes_buttons)
        return result

    def update(self):
        super(ChannelTranslationSelector, self).update()
        if self._controls_to_translate != None:
            for control in self._controls_to_translate:
                control.use_default_message()
                if self.is_enabled():
                    control.set_channel((control.message_channel() + self._mode_index) % 16)

        return
