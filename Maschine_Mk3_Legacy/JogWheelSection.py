# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\JogWheelSection.py
# Compiled at: 2017-09-17 14:21:39
import Live
from _Framework.SubjectSlot import subject_slot
RecordingQuantization = Live.Song.RecordingQuantization
from _Framework.ButtonElement import *
from _Framework.SliderElement import *
from _Framework.CompoundComponent import *
from MidiMap import *
from Constants import *
from Maschine import arm_exclusive
from PadColorButton import IndexedButton

class JogWheelSection(CompoundComponent):
    __encoder_down = False

    def __init__(self, *a, **k):
        super(JogWheelSection, self).__init__(*a, **k)
        self._do_encoder_button.subject = ButtonElement(True, MIDI_CC_TYPE, 0, CC_JOGWHEEL_PUSH)
        self._do_encoder_touch.subject = ButtonElement(True, MIDI_CC_TYPE, 0, CC_JOGWHEEL_TOUCH)
        self._do_encoder_slider.subject = SliderElement(MIDI_CC_TYPE, 0, CC_JOGWHEEL)
        self.__nav_left_button = IndexedButton(True, MIDI_CC_TYPE, CC_NAV_LEFT, 0, (0,
                                                                                    127))
        self.__nav_right_button = IndexedButton(True, MIDI_CC_TYPE, CC_NAV_RIGHT, 0, (0,
                                                                                      127))
        self.__nav_up_button = IndexedButton(True, MIDI_CC_TYPE, CC_NAV_UP, 0, (0,
                                                                                127))
        self.__nav_down_button = IndexedButton(True, MIDI_CC_TYPE, CC_NAV_DOWN, 0, (0,
                                                                                    127))
        self._do_nav_left.subject = self.__nav_left_button
        self._do_nav_right.subject = self.__nav_right_button
        self._do_nav_up.subject = self.__nav_up_button
        self._do_nav_down.subject = self.__nav_down_button
        self._selected_track_change.subject = self.song().view
        self._clip = None
        return

    @subject_slot('value')
    def _do_nav_left(self, value):
        if value > 0:
            self.__nav_left_button.send_index(1)
            self.canonical_parent.navigate(-1, False, False)
        else:
            self.__nav_left_button.send_index(0)

    @subject_slot('value')
    def _do_nav_right(self, value):
        if value > 0:
            self.__nav_right_button.send_index(1)
            self.canonical_parent.navigate(1, False, False)
        else:
            self.__nav_right_button.send_index(0)

    @subject_slot('value')
    def _do_nav_up(self, value):
        if value > 0:
            self.__nav_up_button.send_index(1)
            self.canonical_parent.navigate(-1, True, False)
        else:
            self.__nav_up_button.send_index(0)

    @subject_slot('value')
    def _do_nav_down(self, value):
        if value > 0:
            self.__nav_down_button.send_index(1)
            self.canonical_parent.navigate(1, True, False)
        else:
            self.__nav_down_button.send_index(0)

    @subject_slot('value')
    def _do_encoder_touch(self, value):
        pass

    @subject_slot('value')
    def _do_encoder_button(self, value):
        self.__encoder_down = value > 0

    @subject_slot('value')
    def _do_encoder_slider(self, value):
        self.canonical_parent.navigate(value == 1 and 1 or -1, self.canonical_parent.is_shift_down(), self.__encoder_down)

    @subject_slot('selected_track')
    def _selected_track_change(self):
        pass

    def update(self):
        pass

    def refresh(self):
        pass

    def disconnect(self):
        super(JogWheelSection, self).disconnect()
