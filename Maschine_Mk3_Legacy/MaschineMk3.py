# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\MaschineMk3.py
# Compiled at: 2017-09-20 21:51:33
from __future__ import with_statement
import Live, time
from Maschine import Maschine
from MidiMap import debug_out
from JogWheelSection import JogWheelSection
from _Framework.SubjectSlot import subject_slot
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from StateButton import StateButton
from Constants import *

class MaschineMk3(Maschine):
    """Control Script for Maschine Studio"""
    __module__ = __name__
    _gated_buttons = []

    def __init__(self, c_instance):
        super(MaschineMk3, self).__init__(c_instance)

    def init_type(self):
        """
        Needs to be overridden by specific version to define certain
        specialized behavior
        """
        self._has_stop_button = True

    def _init_maschine(self):
        self.__jog_wheel_section = JogWheelSection()
        self.__metro_tap_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_TAP_METRO_BUTTON, name='Tap_metro_button')
        self._do_tap_metro.subject = self.__metro_tap_button
        self.update_arrange_button()

    def _final_init(self):
        debug_out('########## LIVE 9 MASCHINE Mk3 V 0.50  ############# ')
        super(MaschineMk3, self)._final_init()

    def use_shift_matrix(self):
        return True

    def has_separate_pad_mode_buttons(self):
        return True

    def handle_sysex(self, midi_bytes):
        if len(midi_bytes) > 11 and midi_bytes[0:10] == (240, 0, 33, 9, 22, 0, 77,
                                                         80, 0, 1):
            msg, value = midi_bytes[10:12]
            if msg == 70:
                self.refresh_state()
                self.notify_shift(True)
            elif msg == 77:
                self.notify_shift(value == 1)

    def _click_measure(self):
        pass

    def preferences_name(self):
        return 'MaschineMk3'

    def apply_preferences(self):
        super(MaschineMk3, self).apply_preferences()

    def store_preferences(self):
        super(MaschineMk3, self).store_preferences()

    def _send_midi(self, midi_bytes, **keys):
        self._c_ref.send_midi(midi_bytes)
        time.sleep(0.001)
        return True

    @subject_slot('value')
    def _do_tap_metro(self, value):
        if self.is_shift_down():
            if value == 0:
                return
            self.song().metronome = not self.song().metronome
        else:
            if value != 0:
                self.song().tap_tempo()
            self.__metro_tap_button.send_value(value)

    @subject_slot('value')
    def _do_stop_all(self, value):
        if value != 0:
            if self.isShiftDown():
                self.song().stop_all_clips(0)
            else:
                self.song().stop_all_clips(1)

    def to_color_edit_mode(self, active):
        if self._editsection.is_color_edit() != active:
            self._editsection.set_color_edit(active)

    def cleanup(self):
        for button in self._gated_buttons:
            button.switch_off()
