# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\Maschine.py
# Compiled at: 2017-09-20 23:39:10
from __future__ import with_statement
import Live, time
from functools import partial
from _Framework.Task import Task
from _Framework.SubjectSlot import subject_slot
from PadScale import *
from MidiMap import *
from Constants import *
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement, ON_VALUE, OFF_VALUE
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from _Framework.TransportComponent import TransportComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ToggleComponent import ToggleComponent
from MaschineSessionComponent import MaschineSessionComponent
from MaschineButtonMatrix import MaschineButtonMatrix
from PadColorButton import PadColorButton
from StateButton import StateButton
from ModeHandler import ModeHandler
from MaschineTransport import MaschineTransport
from TrackControlComponent import TrackControlComponent
from EncoderView import EncoderView
LOOP_KNOB_DIVISION = (4.0, 1.0, 0.5)
TRANSPOSE = [-1, 1, -12, 12]

class Maschine(ControlSurface):
    """Basic Control Script for All Maschine Modell Mikro, Mikro Mk2, Mk1, Mk2, Studio"""
    __module__ = __name__
    _has_stop_button = False
    use_shift_pads = False
    __shift_down = False
    __delete_down = False
    __duplicate_down = False
    __select_down = False
    __undo_state = 0
    __redo_state = 0
    __play_button = None
    __nudge_value = 0.25 / 2
    __quantize_setting = 5

    def __init__(self, c_instance):
        super(Maschine, self).__init__(c_instance)
        with self.component_guard():
            register_sender(self)
            self.init_type()
            self._diplay_cache = [
             '', '', '', '']
            self._timed_text = None
            self._suppress_send_midi = True
            self._modifier = None
            self._c_ref = c_instance
            self.display_task = DisplayTask()
            self._challenge = Live.Application.get_random_int(0, 400000000) & 2139062143
            self._active = False
            self._midi_pause_count = 0
            self.blink_state = 0
            self.send_slider_index = 0
            self.nav_index = 0
            self.arm_selected_track = False
            self._set_suppress_rebuild_requests(True)
            self._main_mode_container = ModeHandler(c_instance.note_repeat)
            self._setup_session()
            self.__track_buttons = TrackControlComponent(self._session, self, name='Track_Select_Button_Matrix')
            self.__track_buttons.assign_buttons()
            self._setup_transport()
            self._set_global_buttons()
            self._encoder_section = EncoderView()
            self._init_maschine()
            self._init_settings()
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._on_selected_track_changed()
            self.show_message(str(''))
            self.request_rebuild_midi_map()
            self._set_suppress_rebuild_requests(False)
            self._active = True
            self._display_device_param = False
            self._session.set_track_offset_listener(self.__update_tracks)
            self.set_feedback_channels(FEEDBACK_CHANNELS)
            self._final_init()
            self._main_mode_container.init_elements()
            self._suppress_send_midi = False
            self.apply_preferences()
            self.init_text_display()
        return

    def init_type(self):
        """
        Needs to be overridden by specific version to define certain
        specialized behavior
        """
        pass

    def _init_maschine(self):
        pass

    def _final_init(self):
        self._encoder_section.connect()

    def create_pad_button(self, scene_index, track_index, color_source):
        pass

    def create_gated_button(self, identifier, hue):
        pass

    def apply_preferences(self):
        pref_dict = self._pref_dict

    def store_preferences(self):
        pass

    def _init_settings(self):
        from pickle import loads, dumps
        from encodings import ascii
        nop(ascii)
        preferences = self._c_instance.preferences(self.preferences_name())
        self._pref_dict = {}
        try:
            self._pref_dict = loads(str(preferences))
        except Exception:
            pass

        pref_dict = self._pref_dict
        preferences.set_serializer(lambda : dumps(pref_dict))

    def preferences_name(self):
        return 'Maschine'

    def _pre_serialize(self):
        from pickle import dumps
        from encodings import ascii
        nop(ascii)
        preferences = self._c_instance.preferences('Maschine')
        self.store_preferences()
        dump = dumps(self._pref_dict)
        preferences.set_serializer(lambda : dump)

    def _setup_session(self):
        self._session = MaschineSessionComponent()
        self._matrix = []
        self._bmatrix = MaschineButtonMatrix(4, name='Button_Matrix')
        for sceneIndex in range(4):
            button_row = []
            for trackindex in range(4):
                button = PadColorButton(True, 0, sceneIndex, trackindex, self._main_mode_container)
                button_row.append(button)

            self._matrix.append(tuple(button_row))
            self._bmatrix.add_row(tuple(button_row))

        self._session.set_matrix(self._bmatrix, self._matrix)
        for button, (trackIndex, sceneIndex) in self._bmatrix.iterbuttons():
            if button:
                scene = self._session.scene(sceneIndex)
                clip_slot = scene.clip_slot(trackIndex)
                clip_slot.set_launch_button(button)
                clip_slot.set_triggered_to_play_value(1)
                clip_slot.set_triggered_to_record_value(1)
                clip_slot.set_started_value(1)
                clip_slot.set_recording_value(1)
                clip_slot.set_stopped_value(1)

        for sindex in range(self._session.height()):
            scene = self._session.scene(sindex)
            for cindex in range(self._session.width()):
                clip = scene.clip_slot(cindex)
                clip.set_modifier(self)
                clip.set_index((cindex, sindex))

        self.set_highlighting_session_component(self._session)

    def _set_global_buttons(self):
        self._undo_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_UNDO_BUTTON)
        self._do_undo.subject = self._undo_button
        self._redo_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_REDO_BUTTON)
        self._do_redo.subject = self._redo_button
        self._shift_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_SHIFT_BUTTON)
        self._do_shift.subject = self._shift_button
        self._erase_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_ERASE_BUTTON)
        self._do_erase.subject = self._erase_button
        self._duplicate_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_DUPLICATE_BUTTON)
        self._do_duplicate.subject = self._duplicate_button
        self._selectback_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_BACKSEL_BUTTON)
        self._do_selectback.subject = self._selectback_button
        self._event_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_EVENTS_BUTTON)
        self._do_event_button.subject = self._event_button
        self.__arrange_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_ARRANGE_BUTTON, name='Arrange_button')
        self.__arrange_button.view_mode = VM_SESSION
        self._do_arrange.subject = self.__arrange_button

    def _setup_transport(self):
        is_momentary = True
        transport = TransportComponent()
        self.__play_button = StateButton(is_momentary, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_PLAY_BUTTON, name='Play_Button')
        self.__restart_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_RESTART_BUTTON)
        stop_button = StateButton(not is_momentary, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_STOP_BUTTON, name='Stop_Button')
        self._rec_button = StateButton(is_momentary, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_RECORD_BUTTON, name='Record_Button')
        metrononme_button = StateButton(is_momentary, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_METRONOME_BUTTON, name='Metronome_Button')
        self._song_follow_button = StateButton(is_momentary, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_FOLLOW_BUTTON, name='Follow_Button')
        self._do_rec_button.subject = self._rec_button
        if self._has_stop_button:
            transport.set_play_button(self.__play_button)
            transport.set_stop_button(stop_button)
        else:
            self._hand_play_pressed.subject = self.__play_button
            self._listen_playing.subject = self.song()
        self._stopall_button = StateButton(True, MIDI_CC_TYPE, 0, CC_ALL_BUTTON)
        self._do_stop_all.subject = self._stopall_button
        self._auto_button = StateButton(True, MIDI_CC_TYPE, 0, CC_AUTO_BUTTON, name='Auto_Button')
        self._handle_automation_record.subject = self._auto_button
        self._listen_automation_record.subject = self.song()
        self._handle_restart_button.subject = self.__restart_button
        self._handle_follows_button.subject = self._song_follow_button
        self._follow_song_changed.subject = self.song().view
        transport.set_metronome_button(metrononme_button)
        self._listen_overdub.subject = self.song()

    def toggle_nav_mode(self):
        self._session.switch_step_advance()
        self.show_message(' View Navigation in steps of ' + str(self._session.get_step_advance()))

    def _update_hardware(self):
        self._session.update()
        self.update_undo_redo(True)
        self.__track_buttons.refresh_state()
        self._encoder_section.refresh_state()

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self._update_hardware()

    def _send_midi(self, midi_bytes, **keys):
        self._c_ref.send_midi(midi_bytes)
        return True

    def timed_display(self, text, grid):
        self.timed_message(grid, text, False)

    def init_text_display(self):
        pass

    def _on_selected_track_changed(self):
        super(Maschine, self)._on_selected_track_changed()
        self.set_controlled_track(self.song().view.selected_track)
        self._on_devices_changed.subject = self.song().view.selected_track

    @subject_slot('devices')
    def _on_devices_changed(self):
        pass

    def update(self):
        self.set_feedback_channels(FEEDBACK_CHANNELS)
        super(Maschine, self).update()

    def is_monochrome(self):
        return False

    def has_separate_pad_mode_buttons(self):
        return False

    def get_session(self):
        return self._session

    def handle_track_select(self, track):
        if not track:
            return
        if self.is_delete_down():
            index = vindexof(self.song().tracks, track)
            self.song().delete_track(index)
        else:
            if self.is_duplicate_down():
                index = vindexof(self.song().tracks, track)
                self.song().duplicate_track(index)
            else:
                if self.is_select_down():
                    if track.is_foldable:
                        track.fold_state = track.fold_state == 0 and 1 or 0
                else:
                    if self.is_shift_down():
                        self.song().view.selected_track = track
                    else:
                        self.song().view.selected_track = track
                        arm_exclusive(self.song(), track)

    def get_button_matrix(self):
        return self._bmatrix

    def deassign_matrix(self):
        for scene_index in range(4):
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(None)

        return

    def update_display(self):
        with self.component_guard():
            with self._is_sending_scheduled_messages():
                self._task_group.update(0.1)
            self._main_mode_container.notify(self.blink_state)
            self.__track_buttons.notify(self.blink_state)
            self.blink_state = (self.blink_state + 1) % 4
            self.display_task.tick()
            self.update_undo_redo(False)
            if self.blink_state == 0:
                self.update_arrange_button()

    def handle_notify(self, blink_state):
        pass

    def __update_tracks(self, track_offset):
        self.__track_buttons.assign_buttons()
        self._encoder_section.handle_offset_changed()

    def update_undo_redo(self, force=False):
        if force:
            self.__undo_state = self.song().can_undo
            self.__redo_state = self.song().can_redo
        if self.song().can_undo != self.__undo_state:
            self.__undo_state = self.song().can_undo
            self._undo_button.send_value(self.__undo_state == 1 and 127 or 0)
        if self.song().can_redo != self.__redo_state:
            self.__redo_state = self.song().can_redo
            self._redo_button.send_value(self.__redo_state == 1 and 127 or 0)

    def navigate(self, nav_dir, modifier, alt_modifier=False):
        self._main_mode_container.navigate(nav_dir, modifier, alt_modifier)
        self._encoder_section.navigate(nav_dir, modifier, alt_modifier)

    def handle_edit_action(self, grid, scale=None):
        if not self.is_shift_down():
            return
        if grid == (0, 3):
            if self.song().can_undo == 1:
                self.song().undo()
                self.show_message(str('UNDO'))
        else:
            if grid == (1, 3):
                if self.song().can_redo == 1:
                    self.song().redo()
                    self.show_message(str('REDO'))
            else:
                if grid == (2, 3):
                    clip = self.song().view.detail_clip
                    if clip and clip.is_midi_clip:
                        clip.select_all_notes()
                else:
                    if grid == (3, 3):
                        clip = self.song().view.detail_clip
                        if clip and clip.is_midi_clip:
                            clip.deselect_all_notes()
                    else:
                        if grid == (0, 2) or grid == (1, 2):
                            clip = self.song().view.detail_clip
                            if clip:
                                clip.quantize(QUANT_CONST[self.__quantize_setting], grid[0] == 0 and 1.0 or 0.5)
                                self.show_message('Quantize Clip ' + clip.name + ' by ' + QUANT_STRING[self.__quantize_setting])
                        else:
                            if grid == (2, 2):
                                clip = self.song().view.detail_clip
                                if clip and clip.is_midi_clip:
                                    self.application().view.show_view('Detail/Clip')
                                    nudge_notes_in_clip(clip, clip.get_selected_notes(), self.__nudge_value * -1)
                            else:
                                if grid == (3, 2):
                                    clip = self.song().view.detail_clip
                                    if clip and clip.is_midi_clip:
                                        self.application().view.show_view('Detail/Clip')
                                        nudge_notes_in_clip(clip, clip.get_selected_notes(), self.__nudge_value)
                                else:
                                    if grid == (0, 1):
                                        clip = self.song().view.detail_clip
                                        if clip and clip.is_midi_clip:
                                            clip.replace_selected_notes(tuple([]))
                                    else:
                                        if grid == (1, 1):
                                            clip = self.song().view.detail_clip
                                            if clip:
                                                clip.has_envelopes and clip.clear_all_envelopes()
                                        else:
                                            if grid[1] == 0:
                                                clip = self.song().view.detail_clip
                                                if clip and clip.is_midi_clip:
                                                    track = clip.canonical_parent.canonical_parent
                                                    drum_device = find_drum_device(track)
                                                    if not drum_device:
                                                        notes = clip.get_selected_notes()
                                                        transpose_notes_in_clip(clip, notes, TRANSPOSE[grid[0]], None)
        return

    @subject_slot('is_playing')
    def _listen_playing(self):
        if self.song().is_playing:
            self.__play_button.set_display_value(127, True)
        else:
            self.__play_button.set_display_value(0, True)

    @subject_slot('value')
    def _hand_play_pressed(self, value):
        if value != 0:
            if self.song().is_playing:
                if self.is_shift_down():
                    self.song().start_playing()
                else:
                    self.song().stop_playing()
            else:
                self.song().start_playing()

    @subject_slot('value')
    def _do_undo(self, value):
        if value != 0:
            if self.use_layered_buttons() and self.is_shift_down():
                if self.song().can_redo == 1:
                    self.song().redo()
                    self.show_message(str('REDO'))
            elif self.song().can_undo == 1:
                self.song().undo()
                self.show_message(str('UNDO'))

    @subject_slot('value')
    def _do_redo(self, value):
        if value != 0:
            if self.song().can_redo == 1:
                self.song().redo()
                self.show_message(str('REDO'))

    def handle_modifier(self, value):
        self._main_mode_container.handle_modifier(value)
        self._encoder_section.notify_shift(value)

    def notify_shift(self, value):
        self.__shift_down = value
        self.handle_modifier(self.get_modifier_state())

    @subject_slot('value')
    def _do_shift(self, value):
        self._shift_button.send_value(value)
        self.__shift_down = value > 0
        self.handle_modifier(self.get_modifier_state())

    @subject_slot('value')
    def _do_erase(self, value):
        self._erase_button.send_value(value)
        self.__delete_down = value > 0

    @subject_slot('value')
    def _do_duplicate(self, value):
        self._duplicate_button.send_value(value)
        self.__duplicate_down = value > 0

    @subject_slot('value')
    def _do_selectback(self, value):
        self._selectback_button.send_value(value)
        self.__select_down = value > 0

    @subject_slot('overdub')
    def _listen_overdub(self):
        self._rec_button.set_display_value(self.song().overdub and 127 or 0, True)

    @subject_slot('value')
    def _do_rec_button(self, value):
        if self.is_shift_down():
            if value != 0:
                self.song().overdub = not self.song().overdub
        else:
            self.invoke_rec()

    def invoke_rec(self):
        slot = self.song().view.highlighted_clip_slot
        if slot == None:
            return
        if slot.controls_other_clips:
            slot.fire()
        else:
            if slot.has_clip:
                track = slot.canonical_parent
                if track.can_be_armed:
                    arm_exclusive(self.song(), track)
                self.song().overdub = True
                slot.fire()
            else:
                track = slot.canonical_parent
                if track.can_be_armed:
                    arm_exclusive(self.song(), track)
                    slot.fire()
        return

    @subject_slot('value')
    def _do_fire_button(self, value):
        assert self._fire_button != None
        assert value in range(128)
        if value != 0:
            if self.is_shift_down():
                self.song().tap_tempo()
            else:
                clip_slot = self.song().view.highlighted_clip_slot
                if clip_slot:
                    clip_slot.fire()
        return

    @subject_slot('value')
    def _do_stop_all(self, value):
        self._do_stop_all.send_value(value)
        if value != 0:
            if self.is_shift_down():
                self.song().stop_all_clips(0)
            else:
                self.song().stop_all_clips(1)

    @subject_slot('value')
    def _do_test(self, value):
        pass

    @subject_slot('value')
    def _do_arrange(self, value):
        if value != 0:
            appv = self.application().view
            if appv.is_view_visible('Arranger'):
                self.application().view.show_view('Session')
            else:
                self.application().view.show_view('Arranger')
            self.update_arrange_button()

    def update_arrange_button(self):
        appv = self.application().view
        if appv.is_view_visible('Arranger'):
            if self.__arrange_button.view_mode == VM_SESSION:
                self.__arrange_button.set_display_value(127, True)
                self.__arrange_button.view_mode = VM_ARRANGE
        else:
            if self.__arrange_button.view_mode == VM_ARRANGE:
                self.__arrange_button.set_display_value(0, True)
                self.__arrange_button.view_mode = VM_SESSION

    @subject_slot('session_automation_record')
    def _listen_automation_record(self):
        self._auto_button.set_display_value(self.song().session_automation_record and 127 or 0, True)

    @subject_slot('value')
    def _do_event_button(self, value):
        self._event_button.send_value(value)
        if value != 0:
            if self.is_shift_down():
                clip = self.song().view.detail_clip
                if clip and clip.is_midi_clip:
                    clip.select_all_notes()

    @subject_slot('value')
    def _handle_follows_button(self, value):
        if value != 0:
            self.song().view.follow_song = not self.song().view.follow_song

    @subject_slot('follow_song')
    def _follow_song_changed(self):
        self._song_follow_button.send_value(self.song().view.follow_song and 127 or 0)

    @subject_slot('value')
    def _handle_restart_button(self, value):
        self.__restart_button.send_value(value)
        if value != 0:
            self.song().stop_playing()
            self.song().stop_playing()

    @subject_slot('value')
    def _handle_automation_record(self, value):
        if value > 0:
            self.song().session_automation_record = not self.song().session_automation_record

    def handle_edit(self, clipslotcomp, value):
        self._main_mode_container.handle_edit(clipslotcomp, value)

    def do_midi_launch(self, clipslotcomp, value):
        if self.is_shift_down():
            clipslotcomp._do_launch_clip(value)
        else:
            if clipslotcomp._clip_slot.has_clip:
                clipslotcomp._do_launch_clip(value)
            else:
                clipslotcomp._clip_slot.create_clip(DEFAULT_CLIP_INIT_SIZE)
                clipslotcomp._do_launch_clip(value)

    def is_select_down(self):
        return self.__select_down

    def is_shift_down(self):
        return self.__shift_down

    def is_delete_down(self):
        return self.__delete_down

    def is_duplicate_down(self):
        return self.__duplicate_down

    def get_modifier_state(self):
        return (self.__shift_down and MODIFIER_SHIFT) | (self.__select_down and MODIFIER_SELECT) | (self.__delete_down and MODIFIER_DELETE) | (self.__duplicate_down and MODIFIER_DUPLICATE)

    def get_track_buttons(self):
        return self.__track_buttons

    def in_spec_mode(self):
        """
        If Some Modifier is being held down. This concerns only the grid matrix.
        In Cases where Shift + Pad Button do not call a function (Maschine Studio only)
        Nothing should happen just like with the Maschine Software
        """
        return self.__shift_down or self.__delete_down or self.__duplicate_down

    def use_shift_matrix(self):
        return False

    def use_layered_buttons(self):
        return False

    def to_color_edit_mode(self, active):
        pass

    def clear_display_all(self):
        self.send_to_display('', 0)
        self.send_to_display('', 1)
        self.send_to_display('', 2)
        self.send_to_display('', 3)

    def clear_display(self, grid):
        if self._timed_text:
            self.send_to_display(self._timed_text, grid)
        else:
            self.send_to_display('', grid)

    def timed_message(self, grid, text, hold=False):
        if USE_DISPLAY == False:
            self.show_message(text)
        else:
            if not self.display_task.active(grid):
                self._timed_text = self._diplay_cache[grid]
            self.display_task.set_func(self.clear_display, grid)
            self.send_to_display(text, grid)
            if hold:
                self.display_task.hold()
            self.display_task.start()

    def timed_message_release(self):
        self.display_task.release()

    def update_bank_display(self):
        if USE_DISPLAY:
            name, bank = self._device._current_bank_details()
            if self._display_device_param:
                prms = len(bank)
                d1 = ''
                for i in range(4):
                    parm = bank[i]
                    if parm:
                        name = parm.name
                        d1 += name[:6] + (i < 3 and '|' or '')
                    else:
                        d1 += '      ' + (i < 3 and '|' or '')

                self.send_to_display(d1, 2)
                d1 = ''
                for i in range(4):
                    parm = bank[i + 4]
                    if parm:
                        name = parm.name
                        d1 += name[:6] + (i < 3 and '|' or '')
                    else:
                        d1 += '      ' + (i < 3 and '|' or '')

                self.send_to_display(d1, 4)
            else:
                self.timed_message(2, 'Bank: ' + name)

    def display_parameters(self, paramlist):
        if USE_DISPLAY == False:
            return

    def send_to_display(self, text, grid=0, force=False):
        if USE_DISPLAY == False:
            return
        if not force and self._diplay_cache[grid] == text:
            return
        self._diplay_cache[grid] = text
        if len(text) > 28:
            text = text[:27]
        msgsysex = [240, 0, 0, 102, 23, 18, min(grid, 3) * 28]
        filled = text.ljust(28)
        for c in filled:
            msgsysex.append(ord(c))

        msgsysex.append(247)
        self._send_midi(tuple(msgsysex))

    def cleanup(self):
        pass

    def disconnect(self):
        self._pre_serialize()
        self.clear_display_all()
        for button, (track_index, _) in self._bmatrix.iterbuttons():
            if button:
                button.turn_off()

        time.sleep(0.2)
        self._active = False
        self._suppress_send_midi = True
        super(Maschine, self).disconnect()
        return
