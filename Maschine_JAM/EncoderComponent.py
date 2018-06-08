# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\EncoderComponent.py
# Compiled at: 2018-03-21 20:20:59
import Live
from EncoderHandler import EncoderHandler
from MaschineMode import MaschineMode
from TouchStripSlider import TouchStripSlider
from StateButton import TouchButton
from _Framework.SubjectSlot import subject_slot
from ParameterUtil import EMPTY_PARAM, DEVICE_MAP, DEF_NAME
from MidiMap import SENDS, vindexof, NAV_SRC_ENCODER, toHSB, TSM_PAN, TSM_BAR, TSM_BAR_DOT, TSM_DOT
from ModifierComponent import StateButton, MIDI_CC_TYPE, MASK_CLEAR
ENC_MODE_VOL = 0
ENC_MODE_PAN = 1
ENC_MODE_SENDS = 2
ENC_MODE_DEVICE = 3
EMPTY_CONFIG = [0, 0, 0, 0, 0, 0, 0, 0]

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


class EncoderComponent(MaschineMode):
    __module__ = __name__
    __mode = ENC_MODE_VOL
    __prev_mode = None
    __session = None
    __encoders = None
    __send_offset = 0
    __last_non_step_mode = ENC_MODE_VOL
    __led_msg = None
    __led_msg_dirty = False
    __bar_msg = None
    __bar_msg_dirty = False
    __cfg_msg = None
    __cfg_msg_dirty = False
    __state_listener = None
    __selection_map = {}

    def __init__(self, session, *a, **k):
        super(EncoderComponent, self).__init__(*a, **k)
        self.__session = session
        self.__level_pan_mode_button = StateButton(True, MIDI_CC_TYPE, 0, 91, name='Level_Button')
        self.__handle_level_button.subject = self.__level_pan_mode_button
        self.__send_mode_button = StateButton(True, MIDI_CC_TYPE, 0, 92, name='Aux_Button')
        self.__handle_sends_button.subject = self.__send_mode_button
        self.__device_mode_button = StateButton(True, MIDI_CC_TYPE, 0, 97, name='Control_Button')
        self.__handle_device_button.subject = self.__device_mode_button
        self.__init_led_feedback()
        self.__init_bar_feedback()
        self.__init_config()
        self.__encoders = [ self.create_encoders(index) for index in range(8) ]
        self._return_tracks_change.subject = self.song()
        self._tracks_change.subject = self.song()
        self._handle_track_changed.subject = self.song().view
        self._handle_visble_tracks_changed.subject = self.song()
        self._track = None
        self._device = None
        self.setup_select_track()
        self._device_index = 0
        self._bank_index = 0
        self._nr_of_banks = 0
        self.__device_mode_down = False
        return

    def setup_select_track(self):
        if self._track:
            self._handle_device_changed.subject = None
            self._handle_devices_changed.subject = None
        self._track = self.song().view.selected_track
        if self._track:
            self._device = self._track.view.selected_device
            self._handle_device_changed.subject = self._track.view
            self._handle_devices_changed.subject = self._track
            self._handle_color_changed.subject = self._track
            self._handle_device_changed(True)
            if self._device:
                self._handle_parameters_changed.subject = self._device
            else:
                self._handle_parameters_changed.subject = None
        return

    def set_state_listener(self, listener):
        self.__state_listener = listener

    def _cleanup_mapping(self):
        tracks = self.song().visible_tracks
        cmaps = {}
        keys = self.__selection_map.keys()
        for track in tracks:
            cmaps[track] = True

        for track in keys:
            if track not in cmaps and track in self.__selection_map:
                del self.__selection_map[track]

    @subject_slot('color')
    def _handle_color_changed(self):
        if self._track and self.__mode == ENC_MODE_DEVICE:
            paramlist = self.get_device_parameter()
            self.update_touchstrip_color(paramlist)

    @subject_slot('devices')
    def _handle_devices_changed(self):
        if self._device != self._track.view.selected_device:
            self._handle_device_changed()

    @subject_slot('parameters')
    def _handle_parameters_changed(self):
        if self.__mode == ENC_MODE_DEVICE:
            self.__assign_encoders(False)

    @subject_slot('selected_track')
    def _handle_track_changed(self):
        self.setup_select_track()

    @subject_slot('visible_tracks')
    def _handle_visble_tracks_changed(self):
        self.__assign_encoders(False)
        self._cleanup_mapping()
        if self.__mode == ENC_MODE_VOL:
            self.refresh_state()

    def refresh_state(self):
        for encoder in self.__encoders:
            encoder.refresh()

        self.__led_msg_dirty = True
        self.__bar_msg_dirty = True
        self.update_led()
        self.update_touchstrip_color()

    def _choose_device(self):
        device_list = self._track.devices
        if not device_list or len(device_list) == 0:
            return
        if len(device_list) > 0:
            return device_list[0]
        return

    @subject_slot('selected_device')
    def _handle_device_changed(self, force_change=False):
        self._device = self._track.view.selected_device
        if self._device:
            self._handle_parameters_changed.subject = self._device
        else:
            self._handle_parameters_changed.subject = None
        if self.__mode == ENC_MODE_DEVICE:
            if not self._device:
                self._device = self._choose_device()
                if self._device:
                    self.song().view.select_device(self._device)
            self._bank_index = self._get_stored_bank_index()
            self.__assign_encoders(True)
        return

    def reset_led(self):
        self.__led_msg_dirty = True

    def set_led_value(self, index, val):
        if self.__led_msg[11 + index] != val:
            self.__led_msg[11 + index] = val
            self.__led_msg_dirty = True

    def update_led(self):
        if self.__led_msg_dirty:
            self.canonical_parent._send_midi(tuple(self.__led_msg))
            self.__led_msg_dirty = False

    def __init_config(self):
        self.__cfg_msg = [
         240, 0, 33, 9, 21, 0, 77, 80, 0, 1, 5]
        for _ in range(8):
            self.__cfg_msg.append(0)
            self.__cfg_msg.append(0)

        self.__cfg_msg.append(247)

    def update_bar_config(self):
        for index, encoder in enumerate(self.__encoders):
            mode, color = encoder.get_strip_cfg()
            self.__cfg_msg[11 + index * 2] = mode
            self.__cfg_msg[11 + index * 2 + 1] = color

        if self.canonical_parent:
            self.canonical_parent._send_midi(tuple(self.__cfg_msg))

    def set_bar_config(self, modelist, colorlist):
        assert len(colorlist) == 8
        assert len(modelist) == 8
        for i in range(8):
            self.__cfg_msg[11 + i * 2] = modelist[i]
            self.__cfg_msg[11 + i * 2 + 1] = colorlist[i]

        if self.canonical_parent:
            self.canonical_parent._send_midi(tuple(self.__cfg_msg))

    def set_bar_config_cfglist(self, configlist):
        assert len(configlist) == 8
        for i in range(8):
            mode, color = configlist[i]
            self.__cfg_msg[11 + i * 2] = mode
            self.__cfg_msg[11 + i * 2 + 1] = color

        if self.canonical_parent:
            self.canonical_parent._send_midi(tuple(self.__cfg_msg))

    def turn_off_bars(self):
        self.set_bar_config([0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0])

    def __init_led_feedback(self):
        self.__led_msg = [
         240, 0, 33, 9, 21, 0, 77, 80, 0, 1, 4]
        for _ in range(8):
            self.__led_msg.append(0)

        self.__led_msg.append(247)

    def __init_bar_feedback(self):
        self.__bar_msg = [
         240, 0, 33, 9, 21, 0, 77, 80, 0, 1, 3]
        for _ in range(8):
            self.__bar_msg.append(0)

        self.__bar_msg.append(247)

    def create_encoders(self, index):
        touch = TouchButton(MIDI_CC_TYPE, 0, 20 + index, name='Touch_Tap' + str(index + 1) + '_Control')
        touch.cindex = index
        slider = TouchStripSlider(MIDI_CC_TYPE, 0, 8 + index, index, self, name='Touch_Slider' + str(index + 1) + '_Control')
        slider.cindex = index
        return EncoderHandler(index, slider, touch, self)

    def invoke_nav_left(self):
        if self.__mode == ENC_MODE_DEVICE:
            if self.canonical_parent._modifier.is_select_down():
                self.navigate_device(-1)
            elif self.__device_mode_down:
                self.navigate_chain(-1)
            else:
                self.nav_device_param_banks(-1)
        else:
            if self.__mode == ENC_MODE_SENDS:
                self.nav_send_offset(-1)

    def invoke_nav_right(self):
        if self.__mode == ENC_MODE_DEVICE:
            if self.canonical_parent._modifier.is_select_down():
                self.navigate_device(1)
            elif self.__device_mode_down:
                self.navigate_chain(1)
            else:
                self.nav_device_param_banks(1)
        else:
            if self.__mode == ENC_MODE_SENDS:
                self.nav_send_offset(1)

    def nav_send_offset(self, nav_dir):
        new_pos = self.__send_offset + nav_dir
        if new_pos >= len(self.song().return_tracks) or new_pos < 0:
            return
        self.__send_offset = new_pos
        self.__assign_encoders(False)
        self.canonical_parent.show_message('Control Send ' + str(SENDS[self.__send_offset]))

    def nav_device_param_banks(self, nav_dir):
        prev = self._bank_index
        newpos = min(max(0, prev + nav_dir), self._nr_of_banks - 1)
        if newpos != prev:
            self._bank_index = newpos
            selmap = self._get_selmap()
            if selmap:
                selmap.register_selected_bank(self._device, self._bank_index)
            self.__assign_encoders(True)

    def navigate_device(self, nav_dir):
        device_list = self._track.devices
        if self._device and isinstance(self._device.canonical_parent, Live.Chain.Chain):
            device_list = self._device.canonical_parent.devices
        self.__do_device_nav(vindexof(device_list, self._device), device_list, nav_dir)

    def __do_device_nav(self, index, device_list, nav_dir):
        if index != None and len(device_list) > 1:
            newvalue = min(max(0, index + nav_dir), len(device_list) - 1)
            if newvalue != index:
                self.song().view.select_device(device_list[newvalue])
        return

    def navigate_chain(self, nav_dir):
        if not self._device or not isinstance(self._device.canonical_parent, Live.Chain.Chain):
            return
        my_chain = self._device.canonical_parent
        chain_device = my_chain.canonical_parent
        chain_list = chain_device.chains
        index = vindexof(chain_list, my_chain)
        if index != None and len(chain_list) > 0:
            newvalue = min(max(0, index + nav_dir), len(chain_list) - 1)
            if newvalue != index:
                newchain = chain_list[newvalue]
                device_list = newchain.devices
                if len(device_list) > 0:
                    self.song().view.select_device(device_list[0])
        return

    def navigate(self, nav_dir, modifier, alt_modifier=False, nav_src=NAV_SRC_ENCODER):
        if self.__device_mode_down and self.__mode == ENC_MODE_DEVICE:
            if modifier:
                self.nav_device_param_banks(-nav_dir)
            else:
                device_list = self._track.devices
                index = vindexof(device_list, self._device)
                if index != None:
                    newvalue = min(max(0, index + nav_dir), len(device_list) - 1)
                    if newvalue != index:
                        self.song().view.select_device(device_list[newvalue])
        else:
            self.__assign_encoders(False)
        return

    def notify(self, blink_state):
        pass

    def connect(self):
        self.__assign_encoders()
        self.__send_mode_button.set_display_value(0, True)
        self.__device_mode_button.set_display_value(0, True)
        self.__level_pan_mode_button.set_display_value(127, True)

    def apply_send_offset(self, offset):
        self.__send_offset = offset
        if self.__mode == ENC_MODE_SENDS:
            self.__assign_encoders()

    def gettrack(self, index, off):
        tracks = self.song().visible_tracks
        if index + off < len(tracks):
            return tracks[index + off]
        return

    def set_step_note_levels(self, which, value, grid_control):
        assert which in range(8)

    def get_device_colors(self, parameters):
        colors = [
         0, 0, 0, 0, 0, 0, 0, 0]
        modes = [0, 0, 0, 0, 0, 0, 0, 0]
        if self._device:
            trackcolor = toHSB(self._track.color)[0]
            for i in range(8):
                if i < len(parameters):
                    param_ele = parameters[i]
                    if param_ele != EMPTY_PARAM:
                        param = param_ele[0]
                        if param.min < 0 and abs(param.min) == param.max:
                            modes[i] = TSM_PAN
                            colors[i] = trackcolor
                        else:
                            modes[i] = TSM_BAR
                            colors[i] = trackcolor

        return (
         modes, colors)

    def get_param_list_str(self, paramlist):
        if self._device:
            result = ' Device: ' + self._device.name + ' Params: '
            for i in xrange(0, 8):
                if i < len(paramlist) and paramlist[i] != EMPTY_PARAM:
                    result += ('{}:[{}]  ').format(i + 1, paramlist[i][0].name)
                else:
                    result += ('{}:[----]  ').format(i + 1)

            return result
        return ''

    def get_device_parameter(self):
        mapping = None
        if self._device:
            parmlist = []
            params = self._device.parameters
            if self._device.class_name in DEVICE_MAP:
                mappingObj = DEVICE_MAP[self._device.class_name]
                if isinstance(mappingObj, tuple):
                    mapping = mappingObj
                elif 'params' in mappingObj:
                    mapping = mappingObj['params']
            if mapping != None:
                self._nr_of_banks = len(mapping)
                bank_mapping = mapping[self._bank_index]
                for idx in xrange(0, 8):
                    if bank_mapping != None and idx < len(bank_mapping) and bank_mapping[idx] != None:
                        mp = bank_mapping[idx]
                        if isinstance(mp, tuple):
                            mp_len = len(mp)
                            if mp_len == 4:
                                parmlist.append((self._device.parameters[mp[0]], mp[1], mp[2], mp[3]))
                            elif mp_len == 3:
                                parmlist.append((self._device.parameters[mp[0]], mp[1], mp[2]))
                            elif mp_len == 2:
                                parmlist.append((self._device.parameters[mp[0]], mp[1], None, None))
                        else:
                            parmlist.append(EMPTY_PARAM)

                return parmlist
            self._nr_of_banks = max(0, len(params) - 2) / 8 + 1
            for i in xrange(0, 8):
                idx = self._bank_index * 8 + i + 1
                if idx < len(self._device.parameters):
                    parmlist.append((self._device.parameters[idx], DEF_NAME, None))

            return parmlist
        else:
            return
        return

    def set_encoder_cfg(self, mode_list, color_list):
        for index, encoder in enumerate(self.__encoders):
            encoder.set_encoder_cfg(mode_list[index], color_list[index])

    def get_strip_track_config(self, basemode, trackoffset):
        colors = [0, 0, 0, 0, 0, 0, 0, 0]
        modes = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(8):
            track = self.gettrack(i, trackoffset)
            if track:
                colors[i] = toHSB(track.color)[0]
                modes[i] = basemode
            else:
                colors[i] = 0
                modes[i] = 0

        return (
         modes, colors)

    def update_touchstrip_color(self, paramlist=None):
        trackoff = self.__session.track_offset()
        if self.__mode == ENC_MODE_VOL:
            modes, colors = self.get_strip_track_config(TSM_BAR_DOT, trackoff)
            self.set_encoder_cfg(modes, colors)
            self.update_bar_config()
        else:
            if self.__mode == ENC_MODE_PAN:
                modes, colors = self.get_strip_track_config(TSM_PAN, trackoff)
                self.set_encoder_cfg(modes, colors)
                self.update_bar_config()
            else:
                if self.__mode == ENC_MODE_SENDS:
                    modes, colors = self.get_strip_track_config(TSM_DOT, trackoff)
                    self.set_encoder_cfg(modes, colors)
                    self.update_bar_config()
                else:
                    if self.__mode == ENC_MODE_DEVICE:
                        if paramlist:
                            modes, colors = self.get_device_colors(paramlist)
                            self.set_encoder_cfg(modes, colors)
                            self.update_bar_config()
                        else:
                            self.set_encoder_cfg(EMPTY_CONFIG, EMPTY_CONFIG)
                            self.update_bar_config()

    def update_encoders(self):
        self.__led_msg_dirty = True
        self.__assign_encoders(False)

    def __assign_encoders(self, show_message=True):
        trackoff = self.__session.track_offset()
        paramlist = None
        if self.__mode == ENC_MODE_DEVICE:
            paramlist = self.get_device_parameter()
        self.update_touchstrip_color(paramlist)
        for i in range(8):
            slider = self.__encoders[i]
            track = self.gettrack(i, trackoff)
            if self.__mode in (ENC_MODE_VOL, ENC_MODE_PAN, ENC_MODE_SENDS):
                if track is None:
                    if self.__mode == ENC_MODE_VOL:
                        slider.reset_level_led()
                    slider.assign_parameter(None)
                elif self.__mode == ENC_MODE_VOL:
                    slider.assign_parameter(track.mixer_device.volume, track, True, True)
                elif self.__mode == ENC_MODE_PAN:
                    slider.assign_parameter(track.mixer_device.panning, track)
                elif self.__mode == ENC_MODE_SENDS:
                    slider.assign_parameter(track.mixer_device.sends[self.__send_offset], track)
            elif self.__mode == ENC_MODE_DEVICE:
                if paramlist and i < len(paramlist):
                    if paramlist[i] == EMPTY_PARAM:
                        slider.assign_parameter(None)
                    else:
                        slider.assign_parameter(paramlist[i][0], False)
                else:
                    slider.assign_parameter(None)

        if self.__mode == ENC_MODE_VOL:
            self.update_led()
        if show_message and self.__mode == ENC_MODE_DEVICE:
            if self._device:
                self.canonical_parent.show_message(self.get_param_list_str(paramlist))
        return

    @subject_slot('return_tracks')
    def _return_tracks_change(self):
        if self.__send_offset >= len(self.song().return_tracks):
            self.apply_send_offset(len(self.song().return_tracks) - 1)

    @subject_slot('tracks')
    def _tracks_change(self):
        self.__assign_encoders(False)
        self._cleanup_mapping()

    def is_modifier_down(self):
        return self.canonical_parent._modifier.is_delete_down()

    def is_shift_down(self):
        return self.canonical_parent._modifier.is_shift_down()

    def notify_touch(self, parameter):
        if parameter:
            mode = self.canonical_parent._modifier.modifier_mask()
            if mode == MASK_CLEAR:
                clip_slot = self.song().view.highlighted_clip_slot
                clip = clip_slot.clip
                if clip:
                    clip.clear_envelope(parameter)
                    self.canonical_parent.show_message('Clear Automation for Clip ' + clip.name + ' for Parmeter: ' + parameter.name)

    def __to_mode(self, mode):
        if mode == ENC_MODE_VOL:
            self.__mode = ENC_MODE_VOL
            self.__last_non_step_mode = ENC_MODE_VOL
            self.__assign_encoders(False)
            self.canonical_parent.show_message('Level Mode')
        else:
            if mode == ENC_MODE_PAN:
                self.__mode = ENC_MODE_PAN
                self.__last_non_step_mode = ENC_MODE_PAN
                self.__assign_encoders(False)
                self.canonical_parent.show_message('Pan Mode')
            else:
                if mode == ENC_MODE_SENDS:
                    if self.__mode == ENC_MODE_SENDS:
                        self.__send_offset += 1
                        if self.__send_offset >= len(self.song().return_tracks):
                            self.__send_offset = 0
                    else:
                        self.__send_offset = 0
                    self.__mode = ENC_MODE_SENDS
                    self.__last_non_step_mode = ENC_MODE_SENDS
                    self.__assign_encoders(False)
                    self.canonical_parent.show_message('Control Send ' + str(SENDS[self.__send_offset]))
                else:
                    if mode == ENC_MODE_DEVICE:
                        self.__mode = ENC_MODE_DEVICE
                        self.__last_non_step_mode = ENC_MODE_SENDS
                        self.__assign_encoders(True)

    def __set_radio_buttons(self):
        if self.__mode == ENC_MODE_VOL or self.__mode == ENC_MODE_PAN and (self.__prev_mode != ENC_MODE_VOL or self.__prev_mode != ENC_MODE_PAN):
            self.__send_mode_button.set_display_value(0, True)
            self.__device_mode_button.set_display_value(0, True)
            self.__level_pan_mode_button.set_display_value(127, True)
        else:
            if self.__mode == ENC_MODE_SENDS and self.__prev_mode != ENC_MODE_SENDS:
                self.__send_mode_button.set_display_value(127, True)
                self.__device_mode_button.set_display_value(0, True)
                self.__level_pan_mode_button.set_display_value(0, True)
            else:
                if self.__mode == ENC_MODE_DEVICE and self.__prev_mode != ENC_MODE_DEVICE:
                    self.__send_mode_button.set_display_value(0, True)
                    self.__device_mode_button.set_display_value(127, True)
                    self.__level_pan_mode_button.set_display_value(0, True)

    @subject_slot('value', identify_sender=True)
    def __handle_level_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        self.__prev_mode = self.__mode
        if self.is_shift_down():
            if self.__mode != ENC_MODE_PAN:
                self.__to_mode(ENC_MODE_PAN)
                self.__set_radio_buttons()
        else:
            if self.__mode != ENC_MODE_VOL:
                self.__to_mode(ENC_MODE_VOL)
                self.__set_radio_buttons()

    @subject_slot('value', identify_sender=True)
    def __handle_sends_button(self, value, sender):
        if value == 0 or sender.grabbed:
            return
        self.__prev_mode = self.__mode
        self.__to_mode(ENC_MODE_SENDS)
        self.__set_radio_buttons()

    def _get_selmap(self):
        if self._track not in self.__selection_map:
            self.__selection_map[self._track] = TrackDeviceSelection(self._track)
        return self.__selection_map[self._track]

    def _get_stored_bank_index(self):
        if not self._device:
            return 0
        selmap = self._get_selmap()
        if selmap:
            return selmap.get_bank_index(self._device)
        return 0

    @subject_slot('value', identify_sender=True)
    def __handle_device_button(self, value, sender):
        if sender.grabbed:
            return
        self.__device_mode_down = value != 0
        if self.__state_listener:
            self.__state_listener.notify_state('controldown', self.__device_mode_down)
        if value == 0:
            return
        if not self._device:
            track = self._track
            if track:
                if self._track.devices and len(self._track.devices) > 0:
                    device_list = device_list = self._track.devices
                    sel_device = device_list[0]
                    self.song().view.select_device(sel_device)
                else:
                    return
            else:
                return
        self.__prev_mode = self.__mode
        if self.__mode != ENC_MODE_DEVICE:
            self.__mode = ENC_MODE_DEVICE
            self.__send_mode_button.set_display_value(0, True)
            self.__device_mode_button.set_display_value(127, True)
            self.__level_pan_mode_button.set_display_value(0, True)
            self.__assign_encoders(True)
        else:
            paramlist = self.get_device_parameter()
            self.canonical_parent.show_message(self.get_param_list_str(paramlist))
            if self._device:
                if self.is_shift_down() and isinstance(self._device.canonical_parent, Live.Chain.Chain):
                    chain = self._device.canonical_parent
                    topdevice = chain.canonical_parent
                    self.song().view.select_device(topdevice)
                elif not self.is_shift_down() and self._device.can_have_chains and len(self._device.chains) > 0:
                    device_list = self._device.chains[0].devices
                    self.song().view.select_device(device_list[0])
        self.application().view.show_view('Detail/DeviceChain')
        self.__set_radio_buttons()

    def exit(self):
        pass

    def enter(self):
        pass

    def disconnect(self):
        for encoder in self.__encoders:
            encoder.send_value(0, True)
