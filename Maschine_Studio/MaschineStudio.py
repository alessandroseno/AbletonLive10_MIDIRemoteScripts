# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Studio\MaschineStudio.py
# Compiled at: 2016-02-05 11:51:56
from __future__ import with_statement
import Live, time
from Maschine import Maschine
from JogWheelSection import JogWheelSection
from MIDI_Map import debug_out
from PadColorButton import PadColorButton
from GatedColorButton import GatedColorButton
from _Framework.SubjectSlot import subject_slot
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement

class MaschineStudio(Maschine):
    """Control Script for Maschine Studio"""
    __module__ = __name__
    _gated_buttons = []

    def __init__(self, c_instance):
        super(MaschineStudio, self).__init__(c_instance)

    def create_pad_button(self, scene_index, track_index, color_source):
        return PadColorButton(True, 0, scene_index, track_index, color_source)

    def create_gated_button(self, identifier, hue):
        button = GatedColorButton(True, MIDI_CC_TYPE, identifier, hue)
        self._gated_buttons.append(button)
        return button

    def _init_maschine(self):
        self._jogwheel = JogWheelSection(self._modeselect, self._editsection)
        self.prehear_knob = SliderElement(MIDI_CC_TYPE, 0, 41)
        self.prehear_knob.connect_to(self.song().master_track.mixer_device.cue_volume)
        self._device_component.set_touch_mode(2)

    def _final_init(self):
        debug_out('########## LIVE 9 MASCHINE STUDIO V 2.02 ############# ')

    def _click_measure(self):
        pass

    def preferences_name(self):
        return 'MaschineStudio'

    def apply_preferences(self):
        super(MaschineStudio, self).apply_preferences()
        pref_dict = self._pref_dict
        if 'use_scrub' in pref_dict:
            self._jogwheel.set_scrub_mode(pref_dict['use_scrub'])
        else:
            self._jogwheel.set_scrub_mode(True)
        if 'color_mode' in pref_dict:
            value = pref_dict['color_mode']
            self._session.set_color_mode(value)
            self._session._c_mode_button.send_value(value == True and 127 or 0, True)
        else:
            self._session.set_color_mode(False)
            self._session._c_mode_button.send_value(0, True)

    def _send_midi(self, midi_bytes, **keys):
        self._c_ref.send_midi(midi_bytes)
        time.sleep(0.001)
        return True

    def store_preferences(self):
        super(MaschineStudio, self).store_preferences()
        self._pref_dict['use_scrub'] = self._jogwheel.use_scrub_mode()
        self._pref_dict['color_mode'] = self._session.is_color_mode()

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
