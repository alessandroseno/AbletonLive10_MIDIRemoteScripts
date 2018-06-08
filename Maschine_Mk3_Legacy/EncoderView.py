# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\EncoderView.py
# Compiled at: 2017-09-21 00:13:48
from StateButton import StateButton, TouchButton
from SessionMode import SessionMode
from Encoder import Encoder
from EncoderHandler import EncoderHandler
from MidiMap import *
from Constants import *
from ParameterUtil import *
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from _Framework.InputControlElement import MIDI_CC_TYPE
from __builtin__ import str
ENC_MODE_VOL = 0
ENC_MODE_PAN = 1
ENC_MODE_SENDS = 2
ENC_MODE_DEVICE = 3

def to_display_name(name):
    return filter_umls(name[:6]).ljust(6)


class TrackDeviceSelection:
    __module__ = __name__
    __device_bank_map = {}
    __track = None

    def __init__(self, track, *a, **k):
        self.__track = track

    def register_selected_bank(self, device, bank_index):
        self.__device_bank_map[device] = bank_index

    def get_bank_index(self, device):
        if device in self.__device_bank_map:
            return self.__device_bank_map[device]
        self.__device_bank_map[device] = 0
        return 0


class ButtonHandler(CompoundComponent):
    __track = None

    def __init__(self, index, button, control, *a, **k):
        super(ButtonHandler, self).__init__(*a, **k)
        self._index = index
        self.__button = button
        self._handle_button.subject = button
        self._encoder_control = control
        self._unbind = None
        self._action = None
        self._update = None
        return

    @subject_slot('value')
    def _handle_button(self, value):
        if self._action:
            self._action(value)

    @subject_slot('mute')
    def _handle_mute_changed(self):
        self.__button.send_value(not self.__track.mute and 127 or 0)

    def refresh(self):
        if self._update:
            self._update()

    def deassign_track(self):
        if self._unbind:
            self._unbind()
        self.__track = None
        self._action = None
        self._unbind = None
        self._update = None
        return

    def assign_mute_track(self, track):
        if self._unbind:
            self._unbind()
        self.__track = track
        self._handle_mute_changed.subject = track

        def action(value):
            if value:
                self.__track.mute = not self.__track.mute

        def unbind():
            self._handle_mute_changed.subject = None
            return

        def update():
            if track:
                self.__button.send_value(not self.__track.mute and 127 or 0)
            else:
                self.__button.send_value(0)

        self._action = action
        self._unbind = unbind
        self._update = update
        update()


class EncoderView(CompoundComponent):
    __module__ = __name__
    __mode = ENC_MODE_VOL
    __prev_mode = None
    __session = None
    __encoders = None
    __buttons = None
    __send_offset = 0
    __last_non_step_mode = ENC_MODE_VOL
    __track = None
    __device = None
    __selection_map = {}
    __nr_of_banks = 0
    __bank_index = 0
    __param_list = None
    __plugin_down = False

    def __init__(self, *a, **k):
        super(EncoderView, self).__init__(*a, **k)
        self.__session = self.canonical_parent.get_session()
        self.__encoders = [ self.create_encoders(index) for index in range(8) ]
        self.__buttons = [ self.create_button(index) for index in range(8) ]
        self._return_tracks_change.subject = self.song()
        self._tracks_change.subject = self.song()
        self._handle_track_changed.subject = self.song().view
        self._handle_visble_tracks_changed.subject = self.song()
        self._left_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_LEFT_PAGE_BUTTON)
        self._right_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_RIGHT_PAGE_BUTTON)
        self._mixer_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_MIXER_BUTTON)
        self._plugin_button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, CC_PLUGIN_BUTTON)
        self._handle_left.subject = self._left_button
        self._handle_right.subject = self._right_button
        self._handle_mixer_button.subject = self._mixer_button
        self._handle_plugin_button.subject = self._plugin_button

    def connect(self):
        self.__assign_encoders()
        self.setup_select_track()
        self.light_mode()

    def light_mode(self):
        self._mixer_button.send_value((self.__mode == ENC_MODE_VOL or self.__mode == ENC_MODE_SENDS) and 127 or 0)
        self._plugin_button.send_value(self.__mode == ENC_MODE_DEVICE and 127 or 0)

    def create_encoders(self, index):
        touch = TouchButton(MIDI_CC_TYPE, 0, 10 + index, name='Touch_Tap' + str(index + 1) + '_Control')
        touch.cindex = index
        slider = Encoder(MIDI_CC_TYPE, 0, 70 + index, index, self, name='Encoder' + str(index + 1) + '_Control')
        slider.cindex = index
        return EncoderHandler(index, slider, touch, self)

    def create_button(self, index):
        button = StateButton(True, MIDI_CC_TYPE, BASE_CONTROL_CHANNEL, 22 + index, name='Page_Button_' + str(index + 1) + '_Control')
        button.cindex = index
        return ButtonHandler(index, button, self)

    def gettrack(self, index, off):
        tracks = self.song().visible_tracks
        if index + off < len(tracks):
            return tracks[index + off]
        return

    def notify_shift(self, value):
        pass

    def notify_touch(self, parameter):
        pass

    def is_shift_down(self):
        return self.canonical_parent.is_shift_down()

    def is_modifier_down(self):
        return self.canonical_parent.is_shift_down()

    def set_led_value(self, index, value):
        pass

    def reset_led(self):
        pass

    def navigate(self, nav_dir, modifier, alt_modifier=False, nav_src=NAV_SRC_ENCODER):
        pass

    def handle_offset_changed(self):
        if self.__mode == ENC_MODE_VOL or self.__mode == ENC_MODE_SENDS:
            self.__assign_encoders(False)

    def setup_select_track(self):
        if self.__track:
            self._handle_device_changed.subject = None
            self._handle_devices_changed.subject = None
        self.__track = self.song().view.selected_track
        if self.__track:
            self.__device = self.__track.view.selected_device
            self._handle_device_changed.subject = self.__track.view
            self._handle_devices_changed.subject = self.__track
            self._handle_device_changed(True)
            if self.__device:
                self._handle_parameters_changed.subject = self.__device
            else:
                self._handle_parameters_changed.subject = None
        return

    def refresh_state(self):
        for encoder in self.__encoders:
            encoder.refresh()

        for button in self.__buttons:
            button.refresh()

        self.update_display(None, True)
        return

    @subject_slot('value')
    def _handle_mixer_button(self, value):
        if value == 0:
            return
        if self.__mode == ENC_MODE_VOL:
            self.__mode = ENC_MODE_SENDS
            self.__assign_encoders()
            self.light_mode()
        else:
            if self.__mode == ENC_MODE_SENDS or self.__mode == ENC_MODE_DEVICE:
                self.__mode = ENC_MODE_VOL
                self.__assign_encoders()
                self.light_mode()

    @subject_slot('value')
    def _handle_plugin_button(self, value):
        self.__plugin_down = value > 0
        if value == 0:
            return
        if self.__mode == ENC_MODE_VOL or self.__mode == ENC_MODE_SENDS:
            self.__mode = ENC_MODE_DEVICE
            self.__assign_encoders()
            self.light_mode()
            self.application().view.show_view('Detail/DeviceChain')

    @subject_slot('value')
    def _handle_left(self, value):
        self._left_button.send_value(value)
        if value:
            if self.canonical_parent.is_shift_down():
                if self.__mode == ENC_MODE_SENDS:
                    new_val = self.__send_offset - 1
                    if new_val >= 0:
                        self.__send_offset = new_val
                        self.__assign_encoders()
                elif self.__mode == ENC_MODE_DEVICE:
                    self.navigate_device(-1)
            elif self.__plugin_down and self.__mode == ENC_MODE_DEVICE:
                self.nav_device_param_banks(-1)
            else:
                self.canonical_parent.get_session().bank_left(1)
                self.__assign_encoders()

    @subject_slot('value')
    def _handle_right(self, value):
        self._left_button.send_value(value)
        if value:
            if self.canonical_parent.is_shift_down():
                if self.__mode == ENC_MODE_SENDS:
                    nr_of_ret_tracks = len(self.song().return_tracks)
                    new_val = self.__send_offset + 1
                    if new_val < nr_of_ret_tracks:
                        self.__send_offset = new_val
                        self.__assign_encoders()
                elif self.__mode == ENC_MODE_DEVICE:
                    self.navigate_device(1)
            elif self.__plugin_down and self.__mode == ENC_MODE_DEVICE:
                self.nav_device_param_banks(1)
            else:
                self.canonical_parent.get_session().bank_right(1)
                self.__assign_encoders()

    @subject_slot('return_tracks')
    def _return_tracks_change(self):
        if self.__send_offset >= len(self.song().return_tracks):
            if self.__mode == ENC_MODE_SENDS:
                self.__assign_encoders()

    @subject_slot('tracks')
    def _tracks_change(self):
        self.__assign_encoders(False)
        self._cleanup_mapping()

    @subject_slot('selected_track')
    def _handle_track_changed(self):
        self.setup_select_track()

    @subject_slot('devices')
    def _handle_devices_changed(self):
        if self.__device != self.__track.view.selected_device:
            self._handle_device_changed()

    @subject_slot('selected_device')
    def _handle_device_changed(self, force_change=False):
        self.__device = self.__track.view.selected_device
        if self.__device:
            self._handle_parameters_changed.subject = self.__device
            self._hande_device_name_changed.subject = self.__device
        else:
            self._handle_parameters_changed.subject = None
            self._hande_device_name_changed.subject = None
        if self.__mode == ENC_MODE_DEVICE:
            if not self.__device:
                self.__device = self._choose_device()
                if self.__device:
                    self.song().view.select_device(self.__device)
            self.__bank_index = self._get_stored_bank_index()
            self.__assign_encoders()
            self.update_display()
        return

    @subject_slot('name')
    def _hande_device_name_changed(self):
        if self.__mode == ENC_MODE_DEVICE:
            self.update_display()

    def _choose_device(self):
        device_list = self.__track.devices
        if not device_list or len(device_list) == 0:
            return
        if len(device_list) > 0:
            return device_list[0]
        return

    @subject_slot('parameters')
    def _handle_parameters_changed(self):
        if self.__mode == ENC_MODE_DEVICE:
            self.__assign_encoders(False)

    @subject_slot('visible_tracks')
    def _handle_visble_tracks_changed(self):
        self.__assign_encoders(False)
        self._cleanup_mapping()
        if self.__mode == ENC_MODE_VOL:
            self.refresh_state()

    def _cleanup_mapping(self):
        tracks = self.song().visible_tracks
        cmaps = {}
        keys = self.__selection_map.keys()
        for track in tracks:
            cmaps[track] = True

        for track in keys:
            if track not in cmaps and track in self.__selection_map:
                del self.__selection_map[track]

    def get_param_list_left(self):
        result = ''
        if self.__param_list:
            for i in xrange(0, 4):
                namestr = i < len(self.__param_list) and self.__param_list[i] != EMPTY_PARAM and self.__param_list[i][0].name or ''
                if i < len(self.__param_list) - 1 and i < 3:
                    result += to_display_name(namestr) + '|'
                else:
                    result += to_display_name(namestr)

        return result

    def get_param_list_right(self):
        result = ''
        if self.__param_list:
            for i in xrange(4, 8):
                namestr = i < len(self.__param_list) and self.__param_list[i] != EMPTY_PARAM and self.__param_list[i][0].name or ''
                if i < len(self.__param_list) - 1 and i < 7:
                    result += to_display_name(namestr) + '|'
                else:
                    result += to_display_name(namestr)

        return result

    def get_track_names(self):
        trackoff = self.__session.track_offset()
        track_names = ''
        for i in range(4):
            track = self.gettrack(i, trackoff)
            if self.__mode in (ENC_MODE_VOL, ENC_MODE_PAN, ENC_MODE_SENDS):
                if track is None:
                    track_names += '  --  '
                else:
                    track_names += to_display_name(track.name)
            if i < 3:
                track_names += '|'

        return track_names

    def update_track_names(self):
        if self.__mode in (ENC_MODE_VOL, ENC_MODE_SENDS, ENC_MODE_PAN):
            track_names = self.get_track_names()
            self.canonical_parent.send_to_display(track_names, 2)
            self.canonical_parent.send_to_display(track_names, 3)

    def update_display(self, track_names=None, force=False):
        if self.__mode == ENC_MODE_VOL:
            self.canonical_parent.send_to_display('Level & Mute ', 0, force)
            self.canonical_parent.send_to_display('Pan', 1, force)
            names = track_names is not None and track_names or self.get_track_names()
            self.canonical_parent.send_to_display(names, 2, force)
            self.canonical_parent.send_to_display(names, 3, force)
        else:
            if self.__mode == ENC_MODE_SENDS:
                nr_of_ret_tracks = len(self.song().return_tracks)
                if self.__send_offset < nr_of_ret_tracks:
                    self.canonical_parent.send_to_display('Sends ' + SENDS[self.__send_offset] + ' & Mute ', 0, force)
                else:
                    self.canonical_parent.send_to_display('Sends - & Mute ', 0, force)
                if self.__send_offset + 1 < nr_of_ret_tracks:
                    self.canonical_parent.send_to_display('Sends ' + SENDS[self.__send_offset + 1] + '', 1, force)
                else:
                    self.canonical_parent.send_to_display('', 1, force)
                names = track_names is not None and track_names or self.get_track_names()
                self.canonical_parent.send_to_display(names, 2, force)
                self.canonical_parent.send_to_display(names, 3, force)
            else:
                if self.__mode == ENC_MODE_DEVICE:
                    if self.__device:
                        self.canonical_parent.send_to_display(self.__device.class_name + ':' + filter_umls(self.__device.name), 0, force)
                        self.canonical_parent.send_to_display('', 1, force)
                        self.canonical_parent.send_to_display(self.get_param_list_left(), 2, force)
                        self.canonical_parent.send_to_display(self.get_param_list_right(), 3, force)
                    else:
                        self.canonical_parent.send_to_display('<No Device>', 0, force)
                        self.canonical_parent.send_to_display('', 1, force)
                        self.canonical_parent.send_to_display('', 2, force)
                        self.canonical_parent.send_to_display('', 3, force)
        return

    def __assign_encoders(self, show_message=True):
        trackoff = self.__session.track_offset()
        if self.__mode in (ENC_MODE_VOL, ENC_MODE_PAN, ENC_MODE_SENDS):
            for i in range(4):
                left_enc = self.__encoders[i]
                right_enc = self.__encoders[i + 4]
                left_button = self.__buttons[i]
                track = self.gettrack(i, trackoff)
                if track is None:
                    left_enc.assign_parameter(None)
                    right_enc.assign_parameter(None)
                    left_button.deassign_track()
                else:
                    left_button.assign_mute_track(track)
                    if self.__mode == ENC_MODE_VOL:
                        left_enc.assign_parameter(track.mixer_device.volume, track, True)
                        right_enc.assign_parameter(track.mixer_device.panning, track, True)
                    if self.__mode == ENC_MODE_SENDS:
                        nr_of_ret_tracks = len(self.song().return_tracks)
                        if self.__send_offset < nr_of_ret_tracks:
                            left_enc.assign_parameter(track.mixer_device.sends[self.__send_offset], track, True)
                        else:
                            left_enc.assign_parameter(None)
                        if self.__send_offset + 1 < nr_of_ret_tracks:
                            right_enc.assign_parameter(track.mixer_device.sends[self.__send_offset + 1], track, True)
                        else:
                            right_enc.assign_parameter(None)

        else:
            if self.__mode == ENC_MODE_DEVICE:
                paramlist = self.get_device_parameter()
                self.__param_list = paramlist
                if paramlist:
                    for i in range(8):
                        enc = self.__encoders[i]
                        parm = i < len(paramlist) and paramlist[i] or None
                        if not parm or parm == EMPTY_PARAM:
                            enc.assign_parameter(None)
                        else:
                            enc.assign_parameter(parm[0], False)

                else:
                    for i in range(8):
                        enc = self.__encoders[i]
                        enc.assign_parameter(None)

        self.update_display()
        return

    def get_device_parameter(self):
        mapping = None
        if self.__device:
            parmlist = []
            params = self.__device.parameters
            if self.__device.class_name in DEVICE_MAP:
                mappingObj = DEVICE_MAP[self.__device.class_name]
                if isinstance(mappingObj, tuple):
                    mapping = mappingObj
                elif 'params' in mappingObj:
                    mapping = mappingObj['params']
            if mapping != None:
                self.__nr_of_banks = len(mapping)
                bank_mapping = mapping[self.__bank_index]
                for idx in xrange(0, 8):
                    if bank_mapping != None and idx < len(bank_mapping) and bank_mapping[idx] != None:
                        mp = bank_mapping[idx]
                        if isinstance(mp, tuple):
                            mp_len = len(mp)
                            if mp_len == 4:
                                parmlist.append((self.__device.parameters[mp[0]], mp[1], mp[2], mp[3]))
                            elif mp_len == 3:
                                parmlist.append((self.__device.parameters[mp[0]], mp[1], mp[2]))
                            elif mp_len == 2:
                                parmlist.append((self.__device.parameters[mp[0]], mp[1], None, None))
                        else:
                            parmlist.append(EMPTY_PARAM)

                return parmlist
            self.__nr_of_banks = max(0, len(params) - 2) / 8 + 1
            for i in xrange(0, 8):
                idx = self.__bank_index * 8 + i + 1
                if idx < len(self.__device.parameters):
                    parmlist.append((self.__device.parameters[idx], DEF_NAME, None))

            return parmlist
        else:
            return
        return

    def _get_selmap(self):
        if self.__track not in self.__selection_map:
            self.__selection_map[self.__track] = TrackDeviceSelection(self.__track)
        return self.__selection_map[self.__track]

    def _get_stored_bank_index(self):
        if not self.__device:
            return 0
        selmap = self._get_selmap()
        if selmap:
            return selmap.get_bank_index(self.__device)
        return 0

    def nav_device_param_banks(self, nav_dir):
        prev = self.__bank_index
        newpos = min(max(0, prev + nav_dir), self.__nr_of_banks - 1)
        if newpos != prev:
            self.__bank_index = newpos
            selmap = self._get_selmap()
            if selmap:
                selmap.register_selected_bank(self.__device, self.__bank_index)
            self.__assign_encoders(True)

    def navigate_device(self, nav_dir):
        device_list = self.__track.devices
        if self.__device and isinstance(self.__device.canonical_parent, Live.Chain.Chain):
            device_list = self.__device.canonical_parent.devices
        self.__do_device_nav(vindexof(device_list, self.__device), device_list, nav_dir)

    def __do_device_nav(self, index, device_list, nav_dir):
        if index != None and len(device_list) > 1:
            newvalue = min(max(0, index + nav_dir), len(device_list) - 1)
            if newvalue != index:
                self.song().view.select_device(device_list[newvalue])
        return
