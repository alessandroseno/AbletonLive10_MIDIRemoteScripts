# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\JamModes.py
# Compiled at: 2018-03-20 21:14:23
from __future__ import with_statement
from MidiMap import PARM_RANGE, NAV_SRC_ENCODER, vindexof, arm_exclusive, find_drum_device
from PadMode import PadMode
from DrumMode import DrumMode
from ModifierComponent import MASK_CLEAR, MASK_DUPLICATE, MASK_SELECT, MASK_SHIFT
from StateButton import StateButton, TouchButton
from StepMode import StepMode
from DrumStepMode import DrumStepMode
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from SessionMode import SessionMode
from _Framework.InputControlElement import MIDI_CC_TYPE
from contextlib import contextmanager
from TrackControlComponent import TrackControlComponent
from SceneButtonComponent import SceneButtonComponent
from UserMode import UserMode
from MainEncoderControl import MainEncoderControl, ME_STEP_LEN, ME_PAT_LEN, ME_GRID, ME_NOTE_REPEAT, ME_TEMPO, ME_MASTER, ME_CUE, ME_GROUP
from TouchStripSlider import GrabEncoder
MG_CLIP = 0
MG_STEP = 1
MG_PAD = 2
VM_SESSION = 0
VM_ARRANGE = 1
t = 3.0 / 2.0
CFG_REPEAT_FREQUENCIES = [2, 2 * t, 4, 4 * t, 8, 8 * t, 16, 16 * t, 32, 32 * t, 64]
CFG_REPEAT_DISPLAY = ['1/2', '1/2T', '1/4', '1/4T', '1/8', '1/8T', '1/16', '1/16T', '1/32', '1/32T', '1/64']
del t

def nr_string(nr_index, onlyeven=False):
    if onlyeven:
        return ('  ').join([ idx % 2 == 0 and (idx == nr_index and ('[[{}]]').format(val) or val) or '' for idx, val in enumerate(CFG_REPEAT_DISPLAY) ])
    return ('  ').join([ idx == nr_index and ('[[{}]]').format(val) or val for idx, val in enumerate(CFG_REPEAT_DISPLAY) ])


def calc_new_parm(parm, delta):
    parm_range = parm.max - parm.min
    int_val = int((parm.value - parm.min) / parm_range * PARM_RANGE + 0.1)
    inc_val = min(PARM_RANGE, max(0, int_val + delta))
    return float(inc_val) / float(PARM_RANGE) * parm_range + parm.min


def slot_in_list(clip_slot, slotlist):
    for slot in slotlist:
        if clip_slot == slot:
            return True

    return False


class JamModes(CompoundComponent):
    """
    Class Handling the switch between Modes.
    """
    __module__ = __name__
    __track_buttons = None
    __scene_buttons = None
    __jogwheel_down = False
    __knob_action = None
    __modifier = None
    __step_down = False
    __pad_down = False
    __lock_map = {'step': False}
    __note_repeat_changed = False
    __prev_to_user_mode = None

    def __init__(self, note_repeat=None, *a, **k):
        super(JamModes, self).__init__(*a, **k)
        self._note_repeat = note_repeat
        self.nr_index = 6
        self._note_repeat.repeat_rate = 1.0 / CFG_REPEAT_FREQUENCIES[self.nr_index] * 4.0

        def create_button(ccval, channel=0, cname=None):
            button = StateButton(True, MIDI_CC_TYPE, channel, ccval, name=cname)
            button.last_value = 0
            return button

        self.__main_knob = GrabEncoder(MIDI_CC_TYPE, 0, 86, name='Browse_Control')
        self.__push_button = TouchButton(MIDI_CC_TYPE, 0, 87, name='Browse_Push')
        self.__touch_main = TouchButton(MIDI_CC_TYPE, 0, 88, name='Browse_Touch')
        self._do_main_knob.subject = self.__main_knob
        self._do_push_button.subject = self.__push_button
        self._knob_action = None
        self.__instance_button = create_button(62, 0, 'Instance_1_Button')
        self.__perform_button = create_button(45, 0, 'Perform_Button')
        self.__tune_button = create_button(48, 0, 'Tune_Button')
        self.__swing_button = create_button(49, 0, 'Swing_Button')
        self.__browse_button = create_button(44, 0, 'Browse_Mode_Button')
        self.__do_browse_button.subject = self.__browse_button
        self._arrange_button = create_button(30, 0, 'Song_Mode_Button')
        self._arrange_button.view_mode = VM_SESSION
        self._pad_mode_button = create_button(32, 0, 'Pad_Mode_Button')
        self._step_mode_button = create_button(31, 0, 'Step_Mode_Button')
        self._solo_button = create_button(111, 0, 'Solo_Button')
        self._mute_button = create_button(112, 0, 'Mute_Button')
        self._grid_button = create_button(113, 0, 'Grid_Button')
        self.__notes_button = create_button(46, 0, 'Notes_Button')
        master_button = create_button(60, 0, 'Master_Button')
        group_button = create_button(61, 0, 'Group_Button')
        cue_button = create_button(63, 0, 'Cue_Button')
        self._tempo_button = create_button(110, 0, 'Tempo_Button')
        self._note_repeat_button = create_button(94, 0, 'Note_Repeat_Button')
        self._handle_master_button.subject = master_button
        self._handle_group_button.subject = group_button
        self._handle_cue_button.subject = cue_button
        self._handle_tempo_button.subject = self._tempo_button
        self._tempo_button.selected = False
        self._handle_solo_button.subject = self._solo_button
        self._handle_mute_button.subject = self._mute_button
        self._handle_grid_button.subject = self._grid_button
        self._handle_note_repeat.subject = self._note_repeat_button
        self.__encoder_control = MainEncoderControl(self, master_button, group_button, cue_button, self._grid_button, self._tempo_button, self._note_repeat_button, self._solo_button)
        self.__encoder_control.set_selected_track(self.song().view.selected_track)
        self._clip_mode = SessionMode(0)
        self._pad_mode = PadMode(1)
        self._drum_pad_mode = DrumMode(1)
        self._step_mode = StepMode(2, self._pad_mode)
        self._user_mode = UserMode(4)
        self._drum_step_mode = DrumStepMode(3)
        self._mode_group = MG_CLIP
        self._clip_mode.enter_action = self.enter_clip_mode
        self._pad_mode.enter_action = self.enter_pad_mode
        self._drum_pad_mode.enter_action = self.enter_pad_mode
        self._step_mode.enter_action = self.enter_step_mode
        self._user_mode.enter_action = self.enter_user_mode
        self._do_arrange_button.subject = self._arrange_button
        self._do_pad_mode.subject = self._pad_mode_button
        self._do_step_mode.subject = self._step_mode_button
        self._do_midi_capture.subject = self.__notes_button
        self._mode = self._clip_mode
        self._selected_track_change.subject = self.song().view
        self._detail_clip_changed.subject = self.song().view
        self._capture_changed.subject = self.song()
        self.update_arrange_button()
        self._defer_action = None
        return

    def refresh_state(self):
        self.__encoder_control.update_mode()
        self.__scene_buttons.refresh_state()
        self.__track_buttons.refresh_state()

    def init_elements(self):
        self._light_button(0)
        self.__encoder_control.update_mode()
        self._detect_devices_changed.subject = self.song().view.selected_track
        self.__notes_button.set_display_value(self.song().can_capture_midi and 127 or 0)

    def bind_session(self, matrix_state):
        session = self.canonical_parent.get_session()
        self.__track_buttons = TrackControlComponent(session, self, name='Track_Select_Button_Matrix')
        self.__track_buttons.assign_buttons()
        self.__scene_buttons = SceneButtonComponent(session, name='Scene_Launch_Button_Matrix')
        self.__scene_buttons.assign()
        matrix_state.register_matrix(self.__track_buttons._bmatrix)
        matrix_state.register_matrix(self.__scene_buttons._bmatrix)
        self._step_mode.set_page_handler(self.__scene_buttons)
        self._drum_step_mode.set_page_handler(self.__scene_buttons)
        session.set_track_offset_listener(self.__update_tracks)

    def bind_modify_component(self, modifier_component):
        self.__scene_buttons.bind_modify_component(modifier_component)
        self.__modifier = modifier_component
        self.__modifier.register_shift_listener(self)
        self._pad_mode.set_modifier_component(modifier_component)
        self._drum_pad_mode.set_modifier_component(modifier_component)

    def _light_button(self, which):
        self._pad_mode_button.set_display_value(which == 1 and 127 or 0, True)
        self._step_mode_button.set_display_value(which == 2 and 127 or 0, True)
        self._solo_button.set_display_value(0, True)
        self._mute_button.set_display_value(0, True)
        self._grid_button.set_display_value(0, True)

    @property
    def selected_mode(self):
        return self._mode.ext_name()

    @selected_mode.setter
    def selected_mode(self, value):
        if value == self._mode.ext_name():
            pass
        else:
            if value == 'session_mode':
                self.enter_clip_mode(False)
            else:
                if value == 'pad_mode':
                    self.enter_pad_mode(False)
                else:
                    if value == 'step_mode':
                        self.enter_step_mode(False)
                    else:
                        if value == 'user_mode':
                            self.enter_user_mode(False)

    def handle_track_select(self, track):
        if not track:
            return
        modmask = self.__modifier.modifier_mask()
        if modmask & MASK_CLEAR:
            index = vindexof(self.song().tracks, track)
            self.song().delete_track(index)
        else:
            if modmask & MASK_DUPLICATE:
                index = vindexof(self.song().tracks, track)
                self.song().duplicate_track(index)
            else:
                if modmask & MASK_SELECT:
                    if track.is_foldable:
                        track.fold_state = track.fold_state == 0 and 1 or 0
                else:
                    if modmask & MASK_SHIFT:
                        self.song().view.selected_track = track
                    else:
                        self.song().view.selected_track = track
                        arm_exclusive(self.song(), track)

    def change_mode(self, nextmode):
        return self._mode != nextmode and (self._mode is None or self._mode.is_lock_mode())

    def get_color(self, value, column_index, row_index):
        return self._mode.get_color(value, column_index, row_index)

    def notify(self, blink_state):
        self.__track_buttons.notify(blink_state)
        self._mode.notify(blink_state)
        self.__scene_buttons.notify(blink_state)
        if blink_state == 0:
            self.update_arrange_button()
        if self._defer_action:
            self._defer_action()
            self._defer_action = None
        return

    @subject_slot('selected_track')
    def _selected_track_change(self):
        selected_track = self.song().view.selected_track
        self.__encoder_control.set_selected_track(self.song().view.selected_track)
        self._detect_devices_changed.subject = selected_track
        if self._mode.device_dependent():
            self.__handle_possible_instrument_change()

    @subject_slot('devices')
    def _detect_devices_changed(self):
        self.__handle_possible_instrument_change()

    def __handle_possible_instrument_change(self):
        drum_device = find_drum_device(self.song().view.selected_track)
        if drum_device:
            if self._mode == self._pad_mode:
                self.enter_pad_mode()
            elif self._mode == self._step_mode:
                self.enter_step_mode(False, True)
        else:
            if self._mode == self._drum_pad_mode:
                self.enter_pad_mode()
            else:
                if self._mode == self._drum_step_mode:
                    self.enter_step_mode(False, True)

    @subject_slot('can_capture_midi')
    def _capture_changed(self):
        self.__notes_button.set_display_value(self.song().can_capture_midi and 127 or 0)

    @subject_slot('detail_clip')
    def _detail_clip_changed(self):
        newclip = self.song().view.detail_clip
        if newclip and newclip.is_midi_clip:
            if self._mode == self._step_mode or self._mode == self._drum_step_mode:
                self.enter_step_mode()

    def update_arrange_button(self):
        appv = self.application().view
        if appv.is_view_visible('Arranger'):
            if self._arrange_button.view_mode == VM_SESSION:
                self._arrange_button.set_display_value(127, True)
                self._arrange_button.view_mode = VM_ARRANGE
        else:
            if self._arrange_button.view_mode == VM_ARRANGE:
                self._arrange_button.set_display_value(0, True)
                self._arrange_button.view_mode = VM_SESSION

    @subject_slot('value', identify_sender=True)
    def _do_arrange_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        appv = self.application().view
        if appv.is_view_visible('Arranger'):
            self.application().view.show_view('Session')
        else:
            self.application().view.show_view('Arranger')
        self.update_arrange_button()

    def enter_user_mode(self):
        if self.change_mode(self._user_mode):
            self.__prev_to_user_mode = self._mode
            with self.rebuild():
                self._mode.exit()
                self._mode.spec_unbind()
                self._mode = self._user_mode
                self._light_button(4)
                self._mode.enter()

    def exit_user_mode(self):
        if self._mode == self._user_mode and self.__prev_to_user_mode:
            self.__prev_to_user_mode.enter_action(False)

    def handle_user_mode_removed(self):
        self.exit_user_mode()

    def ensure_reset_note_repeat_mode(self):
        if self._note_repeat.enabled:
            self._note_repeat.enabled = False
            self.__encoder_control.update_note_repeat(0)
            self.__encoder_control.reset_mode()

    def enter_clip_mode(self, show_info=True):
        self.ensure_reset_note_repeat_mode()
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

    def notify_shift(self, shift_value):
        if self._mode == self._pad_mode:
            self._pad_mode.handle_shift(shift_value)
        else:
            if self._mode == self._drum_step_mode:
                self._drum_step_mode.handle_shift(shift_value)
        self.__scene_buttons.notify_shift(shift_value)
        self.__encoder_control.update_mode()

    def is_shift_down(self):
        return self.__modifier.is_shift_down()

    def in_track_mode(self, mode):
        return self.__track_buttons.mode == mode

    def enter_pad_mode(self, show_info=True, check_drum_device=0):
        if show_info:
            self._show_msg_callback('PAD Mode')
        selected_track = self.song().view.selected_track
        if not selected_track or not selected_track.has_midi_input:
            return
        drum_device = find_drum_device(selected_track)
        if drum_device:
            with self.rebuild():
                self._mode.exit()
                self._mode.spec_unbind()
                self._mode = self._drum_pad_mode
                self._light_button(1)
                self._mode.enter()
        else:
            with self.rebuild():
                self._mode.exit()
                self._mode.spec_unbind()
                self._mode = self._pad_mode
                self._light_button(1)
                self._mode.enter()
        self._mode_group = MG_PAD

    def create_clip_on_track(self):
        track = self.song().view.selected_track
        if not track or not track.has_midi_input:
            return
        higlighted_clip_slot = self.song().view.highlighted_clip_slot
        if not higlighted_clip_slot.has_clip:
            higlighted_clip_slot.create_clip(4.0)
        self.song().view.detail_clip = higlighted_clip_slot.clip
        self.application().view.focus_view('Detail/Clip')
        return higlighted_clip_slot.clip

    def enter_step_mode(self, show_info=True, block_clip_creation=False):
        clip = self.song().view.detail_clip
        if not clip and not block_clip_creation:
            clip = self.create_clip_on_track()
        if not clip or not clip.is_midi_clip:
            return
        selected_track = self.song().view.selected_track
        if not selected_track or not selected_track.has_midi_input:
            return
        self.ensure_reset_note_repeat_mode()
        self._light_button(2)
        selected_track = clip.canonical_parent.canonical_parent
        drum_device = find_drum_device(selected_track)
        if drum_device:
            show_info and self._show_msg_callback('Drum Step Mode')
            with self.rebuild():
                if self._mode != self._drum_step_mode:
                    self._mode.exit()
                    self._mode = self._drum_step_mode
                self._light_button(2)
                self._mode.enter()
                self._drum_step_mode.register_page_handler()
                self._defer_action = lambda : self._drum_step_mode.arm_to_clip()
        else:
            show_info and self._show_msg_callback('Step Mode')
            with self.rebuild():
                if self._mode != self._step_mode:
                    self._mode.exit()
                    self._mode = self._step_mode
                self._light_button(2)
                self._mode.enter()
                self._step_mode.register_page_handler()
        self._mode_group = MG_STEP

    @subject_slot('value', identify_sender=True)
    def _do_pad_mode(self, value, sender):
        if sender.grabbed:
            return
        if self.__pad_down and value == 0:
            if self._mode_group != MG_PAD:
                self.enter_pad_mode()
            else:
                self.enter_clip_mode()
                self._mode_group = MG_CLIP
        self.__pad_down = value != 0

    def notify_state(self, state, value):
        if state == 'step' and self._mode_group == MG_STEP:
            self.__lock_map[state] = True

    @subject_slot('value', identify_sender=True)
    def _do_midi_capture(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        if self.song().can_capture_midi:
            self.song().capture_midi()

    @subject_slot('value', identify_sender=True)
    def _do_step_mode(self, value, sender):
        if sender.grabbed:
            return
        if self.__step_down and value == 0:
            if self._mode_group != MG_STEP:
                self.enter_step_mode()
            elif not self.__lock_map['step']:
                self.enter_clip_mode()
                self._mode_group = MG_CLIP
        self.__step_down = value != 0
        if value == 0:
            self.__lock_map['step'] = False
        if self._mode_group == MG_STEP and self.__step_down:
            self.__encoder_control.trigger_mode(ME_STEP_LEN)
        else:
            self.__encoder_control.reset_mode()

    @subject_slot('value', identify_sender=True)
    def _handle_solo_button(self, value, sender):
        if value != 0 or sender.grabbed:
            return
        if self.__modifier.is_shift_down():
            self.__encoder_control.trigger_mode(ME_PAT_LEN)
        else:
            self.__track_buttons.trigger_solo(self._solo_button)

    @subject_slot('value', identify_sender=True)
    def _handle_mute_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        self.__track_buttons.trigger_mute(self._mute_button)

    @subject_slot('value', identify_sender=True)
    def _handle_grid_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        if self.__modifier.is_shift_down():
            self.__track_buttons.trigger_arm(self._grid_button)
        else:
            self.__encoder_control.trigger_mode(ME_GRID)

    def __get_enter_action(self):
        if self._mode_group == MG_CLIP:
            return self.enter_clip_mode
        if self._mode_group == MG_PAD:
            return self.enter_pad_mode
        return self.enter_step_mode

    def change_pattern_length(self, incval, modifier):
        clip = self.song().view.detail_clip
        if clip != None and clip.is_midi_clip:
            newlen = clip.loop_end + incval * (modifier and 1.0 or clip.signature_numerator)
            if newlen > 1.0 and newlen < 128.0:
                clip.loop_end = newlen
                clip.end_marker = newlen
                self.application().view.focus_view('Detail/Clip')
                self.canonical_parent.show_message(' Clip Length ' + str(clip.length))
        return

    def set_nr_value(self, incval, push_down):
        if push_down:
            inc_spec = self.nr_index % 2 == 1 and incval or incval * 2
            self.nr_index = min(max(0, self.nr_index + inc_spec), len(CFG_REPEAT_FREQUENCIES) - 1)
            self._note_repeat.repeat_rate = 1.0 / CFG_REPEAT_FREQUENCIES[self.nr_index] * 4.0
            self.canonical_parent.show_message(' NOTE REPEAT ' + nr_string(self.nr_index, True))
        else:
            self.nr_index = min(max(0, self.nr_index + incval), len(CFG_REPEAT_FREQUENCIES) - 1)
            self._note_repeat.repeat_rate = 1.0 / CFG_REPEAT_FREQUENCIES[self.nr_index] * 4.0
            self.canonical_parent.show_message(' NOTE REPEAT ' + nr_string(self.nr_index))
        self.__note_repeat_changed = True

    @subject_slot('value', identify_sender=True)
    def _handle_note_repeat(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        if not self._note_repeat.enabled:
            self.__encoder_control.trigger_mode(ME_NOTE_REPEAT)
            self.__note_repeat_changed = False
            if self._mode_group != MG_PAD:
                self.__back_action = self.__get_enter_action()
                self.__back_mode = self._mode_group
                self.enter_pad_mode()
            else:
                self.__back_action = None
            if not self._note_repeat.enabled:
                self._note_repeat.enabled = True
            self.canonical_parent.show_message(' NOTE REPEAT ' + nr_string(self.nr_index))
            self.__encoder_control.update_note_repeat(127)
        else:
            self._note_repeat.enabled = False
            self.__encoder_control.reset_mode()
            self.__encoder_control.update_note_repeat(0)
            if self.__back_action:
                self.__back_action()
                self._mode_group = self.__back_mode
        return

    @subject_slot('value', identify_sender=True)
    def _handle_tempo_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        if self.__modifier.is_shift_down():
            self.song().tap_tempo()
        else:
            self.__encoder_control.trigger_mode(ME_TEMPO)

    @subject_slot('value', identify_sender=True)
    def _handle_master_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        self.__encoder_control.trigger_mode(ME_MASTER)

    @subject_slot('value', identify_sender=True)
    def _handle_cue_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        self.__encoder_control.trigger_mode(ME_CUE)

    @subject_slot('value', identify_sender=True)
    def _handle_group_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        self.__encoder_control.trigger_mode(ME_GROUP)

    @subject_slot('value')
    def _do_main_knob(self, value):
        if not self.__main_knob.is_grabbed:
            self.__encoder_control.handle_encoder(value == 127 and -1 or 1, self.__jogwheel_down)

    @subject_slot('value', identify_sender=True)
    def _do_push_button(self, value, sender):
        if not sender.grabbed:
            self.__jogwheel_down = value > 0

    @subject_slot('value', identify_sender=True)
    def __do_browse_button(self, value, sender):
        if sender.grabbed:
            return
        browsedown = value != 0
        self.__browse_button.set_display_value(value)
        self.__modifier.set_browse_down(browsedown)
        modmask = self.__modifier.modifier_mask()
        if browsedown and modmask & MASK_SHIFT:
            self.song().stop_all_clips(1)
        else:
            if browsedown:
                self.__track_buttons.trigger_stop()
            else:
                self.__track_buttons.trigger_to_prev()

    @contextmanager
    def rebuild(self):
        self.canonical_parent._set_suppress_rebuild_requests(True)
        yield
        self.canonical_parent._set_suppress_rebuild_requests(False)
        self.canonical_parent.request_rebuild_midi_map()

    def __update_tracks(self, track_offset):
        self.__track_buttons.assign_buttons()
        self.canonical_parent._encoder_modes.update_encoders()

    def navigate(self, direction, modifier, alt_modifier=False, nav_source=NAV_SRC_ENCODER):
        self._mode.navigate(direction, modifier, alt_modifier, nav_source)
        self.__scene_buttons.assign()
        if self._mode_group == MG_CLIP:
            return True
        self.__track_buttons.assign_buttons()
        return False
