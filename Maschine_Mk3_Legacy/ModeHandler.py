# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\ModeHandler.py
# Compiled at: 2017-09-17 12:20:39
from __future__ import with_statement
import sys
from contextlib import contextmanager
from StateButton import StateButton, TouchButton
from SessionMode import SessionMode
from MidiMap import *
from Constants import *
from SceneMode import SceneMode
from PadMode import PadMode
from DrumMode import DrumMode
from TrackMode import TrackMode, LevelIndicatorMode
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from _Framework.InputControlElement import MIDI_CC_TYPE
MG_CLIP = 0
MG_STEP = 1
MG_PAD = 2
MG_TRACK = 3
MG_LED = 4
t = 3.0 / 2.0
NOTE_REPEAT_FREQUENCIES = [32 * t,
 32,
 16 * t,
 16,
 8 * t,
 8,
 4 * t,
 4]
CFG_REPEAT_FREQUENCIES = [2, 2 * t, 4, 4 * t, 8, 8 * t, 16, 16 * t, 32, 32 * t, 64]
CFG_REPEAT_DISPLAY = ['1/2', '1/2T', '1/4', '1/4T', '1/8', '1/8T', '1/16', '1/16T', '1/32', '1/32T', '1/64']
CTRL_TO_FREQ = (
 (40, 4),
 (
  45, 4 * t),
 (41, 8),
 (
  46, 8 * t),
 (42, 16),
 (
  47, 16 * t),
 (43, 32),
 (
  48, 32 * t),
 (44, 64))
CTRL_CFG_TO_FREQ = ((100, 1),
 (101, 2),
 (102, 3),
 (103, 4))
del t
TRANSPOSE = [
 -1, 1, -12, 12]

class ModeHandler(CompoundComponent):
    """
    Class Handling the switch between Modes.
    """
    __module__ = __name__
    __jogwheel_down = False
    __knob_action = None
    __modifier = None
    __step_down = False
    __pad_down = False
    __lock_map = {'step': False}
    __note_repeat_changed = False
    __prev_to_user_mode = None
    __return_mode = None
    _clip_mode_down = False

    def __init__(self, note_repeat=None, *a, **k):
        super(ModeHandler, self).__init__(*a, **k)
        self._note_repeat = note_repeat
        self.nr_index = 6
        self._note_repeat.repeat_rate = 1.0 / CFG_REPEAT_FREQUENCIES[self.nr_index] * 4.0

        def create_button(ccval, channel=0, cname=None):
            button = StateButton(True, MIDI_CC_TYPE, channel, ccval, name=cname)
            button.last_value = 0
            return button

        self._note_repeat_button = create_button(CC_NOTE_REPEAT_BUTTON, 0, 'Note_Repeat_Button')
        self._do_note_repeat.subject = self._note_repeat_button
        self._scene_mode_button = create_button(CC_SCENE_BUTTON, 0, 'Scene_Mode_Button')
        self._clip_mode_button = create_button(CC_PATTERN_BUTTON, 0, 'Pattern_Mode_Button')
        self._pad_mode_button = create_button(CC_PAD_BUTTON, 0, 'Pad_Mode_Button')
        self._keyboard_mode_button = create_button(CC_KEYBOARD_BUTTON, 0, 'Keyboard_Mode_Button')
        self._track_mode_button = create_button(CC_MIKRO_GROUP_BUTTON, 0, 'Track_Mode_Button')
        self._level_mode_button = create_button(120, 0, 'Level_Mode_Button')
        self._select_clip_mode.subject = self._clip_mode_button
        self._select_scene_mode.subject = self._scene_mode_button
        self._select_pad_mode.subject = self._pad_mode_button
        self._select_keyboard_mode.subject = self._keyboard_mode_button
        self._select_track_mode.subject = self._track_mode_button
        self._select_level_mode.subject = self._level_mode_button
        self._solo_button = create_button(CC_SOLO_BUTTON, 0, 'Solo_Button')
        self._mute_button = create_button(CC_MUTE_BUTTON, 0, 'Mute_Button')
        self._select_button = create_button(CC_SELECT_BUTTON, 0, 'Select_Button')
        self._handle_solo_button.subject = self._solo_button
        self._handle_mute_button.subject = self._mute_button
        self._handle_select_button.subject = self._select_button
        self._clip_mode = SessionMode()
        self._scene_mode = SceneMode()
        self._pad_mode = PadMode()
        self._drum_mode = DrumMode()
        self._track_mode = TrackMode()
        self._level_mode = LevelIndicatorMode()
        self._pad_mode.fitting_mode = self.fitting_mode
        self._drum_mode.fitting_mode = self.fitting_mode
        self._mode_group = MG_CLIP
        self._clip_mode.button_index = CLIP_MODE
        self._scene_mode.button_index = SCENE_MODE
        self._pad_mode.button_index = PAD_MODE
        self._drum_mode.button_index = PAD_MODE
        self._track_mode.button_index = TRACK_MODE
        self._level_mode.button_index = LEVEL_MODE
        self._clip_mode.enter_action = self.enter_clip_mode
        self._scene_mode.enter_action = self.enter_scene_mode
        self._pad_mode.enter_action = self.enter_pad_mode
        self._track_mode_button.send_value(7)
        self._mode = self._clip_mode
        self._selected_track_change.subject = self.song().view
        self._detail_clip_changed.subject = self.song().view
        self._defer_action = None
        self.__selected_track = self.song().view.selected_track
        if self.__selected_track:
            self.__on_track_color_changed.subject = self.__selected_track
        else:
            self.__on_track_color_changed.subject = None
        self.nr_frq = CTRL_TO_FREQ[4][1]
        self._note_repeat.repeat_rate = 1.0 / self.nr_frq * 4.0
        self._track_color = toHSB(self.song().view.selected_track.color)
        return

    def refresh_state(self):
        self.__encoder_control.update_mode()

    def init_shift_handler(self):
        pass

    def _light_button(self, which):
        self._scene_mode_button.send_value(which == SCENE_MODE and 1 or 0, True)
        self._clip_mode_button.send_value(which == CLIP_MODE and 1 or 0, True)
        if self.canonical_parent.has_separate_pad_mode_buttons():
            if self._mode == self._drum_mode:
                self._pad_mode_button.send_value(which == PAD_MODE and 1 or 0, True)
                self._keyboard_mode_button.send_value(0, True)
            else:
                self._keyboard_mode_button.send_value(which == PAD_MODE and 1 or 0, True)
                self._pad_mode_button.send_value(0, True)
        else:
            self._pad_mode_button.send_value(which == PAD_MODE and 1 or 0, True)
        self._level_mode_button.send_value(which == LEVEL_MODE and 1 or 0, True)
        self._track_mode_button.send_value(which == TRACK_MODE and self._track_color[0] or self._track_color[1], True)

    def init_elements(self):
        self._light_button(CLIP_MODE)
        self._track_mode.init_elements()
        self._level_mode.init_elements()
        self._detect_devices_changed.subject = self.song().view.selected_track

    def navigate(self, direction, modifier, alt_modifier=False):
        self._mode.navigate(direction, modifier, alt_modifier)

    def bind_modify_component(self, modifier_component):
        pass

    def is_shift_down(self):
        return self.canonical_parent.is_shift_down()

    def get_modifier_state(self):
        return self.canonical_parent.get_modifier_state()

    def handle_modifier(self, value):
        if self.canonical_parent.use_shift_matrix():
            self._mode.handle_shift(value & 1 != 0)

    def handle_edit(self, clipslotcomp, value):
        if value == 0:
            return
        if self._mode == self._clip_mode and self.canonical_parent.is_duplicate_down():
            if self.canonical_parent.is_shift_down():
                self.double_clipslot(clipslotcomp._clip_slot)
            else:
                self.__handle_duplicate(clipslotcomp)
        else:
            if self._mode == self._clip_mode and self.canonical_parent.is_delete_down():
                self.__handle_delete(clipslotcomp)
            else:
                if self.canonical_parent.is_shift_down():
                    if self.canonical_parent.use_shift_matrix():
                        self.canonical_parent.handle_edit_action(clipslotcomp.get_index())

    def double_clipslot(self, clip_slot):
        song = self.song()
        track = clip_slot.canonical_parent
        if clip_slot.clip is not None and track.has_midi_input:
            clip = clip_slot.clip
            if clip.length <= 2048.0:
                clip.duplicate_loop()
                self.canonical_parent.show_message('Double Loop : ' + str(int(clip.length / 4)) + ' Bars')
                song.view.detail_clip = clip
                self.application().view.focus_view('Detail/Clip')
            else:
                self.canonical_parent.show_message('Clip is to long to Duplicate')
        return

    def __handle_delete(self, clipslotcomp):
        if clipslotcomp._clip_slot is None:
            return
        if self.is_shift_down():
            pass
        else:
            clipslotcomp._do_delete_clip()
        return

    def __handle_duplicate(self, clipslotcomp):
        if clipslotcomp._clip_slot is None:
            return
        if self.is_shift_down():
            pass
        else:
            self.duplicate_clip_slot(clipslotcomp._clip_slot)
        return

    def duplicate_clip_slot(self, clip_slot):
        if clip_slot.has_clip:
            try:
                track = clip_slot.canonical_parent
                index = list(track.clip_slots).index(clip_slot)
                track.duplicate_clip_slot(index)
                self.canonical_parent.show_message('Duplicate Clip ' + clip_slot.clip.name)
                select_clip_slot(self.song(), track.clip_slots[index + 1])
            except Live.Base.LimitationError:
                pass
            except RuntimeError:
                pass

    def get_color(self, value, column_index, row_index):
        return self._mode.get_color(value, column_index, row_index)

    def change_mode(self, nextmode):
        return self._mode != nextmode and (self._mode == None or self._mode.is_lock_mode())

    @subject_slot('value')
    def _select_clip_mode(self, value):
        click = value != 0
        if click:
            if self.change_mode(self._clip_mode):
                with self.rebuild():
                    self._mode.exit()
                    self._mode = self._clip_mode
                    self._light_button(CLIP_MODE)
                    self._mode.enter()
        self._clip_mode_down = click

    def in_pad_mode(self):
        return self._mode == self._pad_mode or self._mode == self._drum_mode

    @subject_slot('value')
    def _do_note_repeat(self, value):
        if value == 0:
            self._note_repeat_button.send_value(0)
            self._note_repeat.enabled = False
            if self.__return_mode != None:
                self._enter_mode(self.__return_mode)
                self.__return_mode = None
        else:
            self._note_repeat_button.send_value(127)
            self._note_repeat.enabled = True
            if not self.in_pad_mode():
                self.__return_mode = self._mode
                self._select_pad_mode(1)
        return

    def _return_to_mode(self):
        if self.__return_mode:
            self._enter_mode(self.__return_mode)
            self.__return_mode = None
        return

    def _enter_mode(self, mode):
        if self.change_mode(mode):
            with self.rebuild():
                self._mode.exit()
                self._mode = mode.fitting_mode(self.song().view.selected_track)
                self._light_button(self._mode.button_index)
                self._mode.enter()

    @subject_slot('value')
    def _select_scene_mode(self, value):
        if value != 0:
            if self.change_mode(self._scene_mode):
                with self.rebuild():
                    self._mode.exit()
                    self._mode = self._scene_mode
                    self._light_button(SCENE_MODE)
                    self._mode.enter()

    @subject_slot('value')
    def _select_keyboard_mode(self, value):
        if value != 0:
            if self.change_mode(self._pad_mode):
                track = self.song().view.selected_track
                newmode = self.fitting_mode(track)
                with self.rebuild():
                    self._mode.exit()
                    self._mode = newmode
                    self._light_button(PAD_MODE)
                    self._mode.enter()

    @subject_slot('value')
    def _select_pad_mode(self, value):
        if value != 0:
            if self.change_mode(self._pad_mode):
                track = self.song().view.selected_track
                newmode = self.fitting_mode(track)
                with self.rebuild():
                    self._mode.exit()
                    self._mode = newmode
                    self._light_button(PAD_MODE)
                    self._mode.enter()

    @subject_slot('value')
    def _select_level_mode(self, value):
        if value == 0:
            self._return_to_mode()
        else:
            self.__return_mode = self._mode
            self._enter_mode(self._level_mode)

    @subject_slot('value')
    def _select_track_mode(self, value):
        if value == 0:
            self._return_to_mode()
        else:
            self.__return_mode = self._mode
            self._enter_mode(self._track_mode)

    def enter_scene_mode(self, show_info=True):
        pass

    def enter_pad_mode(self, show_info=True):
        pass

    def enter_clip_mode(self, show_info=True):
        if self.change_mode(self._clip_mode):
            if show_info:
                try:
                    self._show_msg_callback('SESSION VIEW Mode')
                except:
                    pass

            with self.rebuild():
                self._mode.exit()
                self._mode.spec_unbind()
                self._mode = self._clip_mode
                self._light_button(0)
                self._mode.enter()

    def fitting_mode(self, track):
        if not track:
            return self._pad_mode
        drum_device = find_drum_device(track)
        if drum_device != None:
            return self._drum_mode
        return self._pad_mode

    @subject_slot('color')
    def __on_track_color_changed(self):
        if self._mode == self._pad_mode:
            self._pad_mode.update_color()

    @subject_slot('selected_track')
    def _selected_track_change(self):
        selected_track = self.song().view.selected_track
        if selected_track:
            self._track_color = toHSB(selected_track.color)
            self._track_mode_button.send_value(self._mode.get_mode_id() == TRACK_MODE and self._track_color[0] or self._track_color[1], True)
        if self._mode == self._pad_mode or self._mode == self._drum_mode:
            newmode = self.fitting_mode(selected_track)
            if newmode != self._mode:
                with self.rebuild():
                    self._mode.exit()
                    self._mode = newmode
                    self._light_button(PAD_MODE)
                    self._mode.enter()
            else:
                self._mode.update_selected_track()

    @subject_slot('detail_clip')
    def _detail_clip_changed(self):
        newclip = self.song().view.detail_clip
        if newclip and newclip.is_midi_clip:
            pass

    @subject_slot('devices')
    def _detect_devices_changed(self):
        pass

    @subject_slot('value')
    def _handle_solo_button(self, value):
        if self.is_shift_down():
            pass
        else:
            self.canonical_parent.get_track_buttons().trigger_solo(self._solo_button, value)

    @subject_slot('value')
    def _handle_mute_button(self, value):
        if self.is_shift_down():
            pass
        else:
            self.canonical_parent.get_track_buttons().trigger_mute(self._mute_button, value)

    @subject_slot('value')
    def _handle_select_button(self, value):
        self._select_button.send_value(value, True)
        if value == 0:
            self.canonical_parent.get_track_buttons().trigger_to_prev()
        else:
            self.canonical_parent.get_track_buttons().trigger_stop()

    @contextmanager
    def rebuild(self):
        self.canonical_parent._set_suppress_rebuild_requests(True)
        yield
        self.canonical_parent._set_suppress_rebuild_requests(False)
        self.canonical_parent.request_rebuild_midi_map()

    def notify(self, blink_state):
        self._mode.notify(blink_state)
