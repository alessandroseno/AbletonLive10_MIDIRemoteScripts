# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mikro_Mk2\MaschineMikroMk2.py
# Compiled at: 2016-02-05 11:51:57
from __future__ import with_statement
import Live, time
from Maschine import Maschine
from MaschineMixerComponent import MaschineMixerComponent
from MIDI_Map import debug_out
from KnobSection import KnobSection
from PadColorButton import PadColorButton
from GatedColorButton import GatedColorButton
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement, ON_VALUE, OFF_VALUE
from _Framework.ButtonMatrixElement import ButtonMatrixElement

class MaschineMikroMk2(Maschine):
    """Control Script for Maschine Studio"""
    __module__ = __name__
    _gated_buttons = []

    def __init__(self, c_instance):
        super(MaschineMikroMk2, self).__init__(c_instance)

    def create_pad_button(self, scene_index, track_index, color_source):
        return PadColorButton(True, 0, scene_index, track_index, color_source)

    def create_gated_button(self, identifier, hue):
        button = GatedColorButton(True, MIDI_CC_TYPE, identifier, hue)
        self._gated_buttons.append(button)
        return button

    def _init_maschine(self):
        self._jogwheel = KnobSection(self._modeselect, self._editsection)
        self._note_repeater.registerKnobHandler(self._jogwheel)
        self._mixer.set_touch_mode(2)
        self._device_component.set_touch_mode(2)

    def to_color_edit_mode(self, active):
        if self._editsection.is_color_edit() != active:
            self._jogwheel.invoke_color_mode(active and 1 or 0)

    def use_layered_buttons(self):
        return True

    def _final_init(self):
        debug_out('########## LIVE 9 MASCHINE Mikro Mk2 V 2.0.0 ############# ')

    def _click_measure(self):
        pass

    def _send_midi(self, midi_bytes, **keys):
        self._c_ref.send_midi(midi_bytes)
        if self._midi_pause_count == 1:
            time.sleep(0.002)
            self._midi_pause_count = 0
        else:
            self._midi_pause_count = self._midi_pause_count + 1
        return True

    def apply_preferences(self):
        super(MaschineMikroMk2, self).apply_preferences()
        pref_dict = self._pref_dict
        if 'color_mode' in pref_dict:
            value = pref_dict['color_mode']
            self._session.set_color_mode(value)
            self._session._c_mode_button.send_value(value == True and 127 or 0, True)
        else:
            self._session.set_color_mode(False)
            self._session._c_mode_button.send_value(0, True)

    def store_preferences(self):
        super(MaschineMikroMk2, self).store_preferences()
        self._pref_dict['color_mode'] = self._session.is_color_mode()

    def preferences_name(self):
        return 'MaschineMikroMk2'

    def cleanup(self):
        for button in self._gated_buttons:
            button.switch_off()
