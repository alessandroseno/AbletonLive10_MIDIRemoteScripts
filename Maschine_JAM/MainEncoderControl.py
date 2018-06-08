# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\MainEncoderControl.py
# Compiled at: 2018-03-21 20:20:59
from __future__ import with_statement
from MidiMap import SEL_MODE_ARM, SEL_MODE_SOLO, CLIQ_DESCR, calc_new_parm
ME_MASTER = 0
ME_GROUP = 1
ME_CUE = 2
ME_GRID = 3
ME_TEMPO = 4
ME_NOTE_REPEAT = 5
ME_STEP_LEN = 6
ME_PAT_LEN = 7

class MainEncoderControl:
    __master_button = None
    __group_button = None
    __cue_button = None
    __grid_button = None
    __tempo_button = None
    __solo_button = None
    __mode = ME_MASTER
    __last_mode = ME_MASTER
    __action_map = {}
    __selected_track = None
    __song = None
    __back_action = None
    __back_mode = None

    def __init__(self, jam_mode, master, group, cue, grid, tempo, note_repeat, solo):
        self.__song = jam_mode.song()
        self.__parent = jam_mode
        self.__master_button = master
        self.__cue_button = cue
        self.__grid_button = grid
        self.__group_button = group
        self.__tempo_button = tempo
        self.__note_repeat_button = note_repeat
        self.__solo_button = solo
        self._encoder_action = self.__do_master
        self.__action_map = {ME_MASTER: self.__do_master, ME_TEMPO: self.__do_tempo, ME_GRID: self.__do_grid, 
           ME_CUE: self.__do_cue, ME_GROUP: self.__do_group, ME_NOTE_REPEAT: self.__do_note_repeat, 
           ME_STEP_LEN: self.__do_step_len, ME_PAT_LEN: self.__do_pat_len}

    def update_mode(self):
        self.__master_button.set_display_value(self.__mode == ME_MASTER and 127 or 0, True)
        self.__cue_button.set_display_value(self.__mode == ME_CUE and 127 or 0, True)
        self.__group_button.set_display_value(self.__mode == ME_GROUP and 127 or 0, True)
        self.__tempo_button.set_display_value(self.__mode == ME_TEMPO and 127 or 0, True)
        if self.__parent.is_shift_down():
            self.__grid_button.set_display_value(self.__parent.in_track_mode(SEL_MODE_ARM) and 127 or 0, True)
            self.__solo_button.set_display_value(self.__mode == ME_PAT_LEN and 127 or 0, True)
        else:
            self.__grid_button.set_display_value(self.__mode == ME_GRID and 127 or 0, True)
            self.__solo_button.set_display_value(self.__parent.in_track_mode(SEL_MODE_SOLO) and 127 or 0, True)
        self._encoder_action = self.__action_map[self.__mode]

    def trigger_mode(self, mode):
        if mode in (ME_PAT_LEN, ME_GRID, ME_TEMPO, ME_NOTE_REPEAT):
            if self.__mode == mode:
                self.reset_mode()
            else:
                self.__mode = mode
                self.update_mode()
        else:
            self.__last_mode = mode
            self.__mode = mode
            self.update_mode()

    def update_note_repeat(self, value):
        self.__note_repeat_button.set_display_value(value, True)

    def reset_mode(self):
        self.__mode = self.__last_mode
        self.__tempo_button.selected = False
        self.__grid_button.selected = False
        self.update_mode()

    def __do_grid(self, value, push_down):
        quant = self.__song.clip_trigger_quantization
        self.__song.clip_trigger_quantization = max(0, min(13, quant + value))
        self.__parent.canonical_parent.show_message('Clip Quantize ' + CLIQ_DESCR[self.__song.clip_trigger_quantization])

    def __do_note_repeat(self, value, push_down):
        self.__parent.set_nr_value(value, push_down)

    def __do_step_len(self, value, push_down):
        self.__parent._step_mode.adjust_step_len(value, push_down)

    def __do_pat_len(self, value, push_down):
        self.__parent.change_pattern_length(value, push_down)

    def set_selected_track(self, track):
        self.__selected_track = track

    def __do_group(self, value, push_down):
        if self.__selected_track:
            delta = push_down and value or value * 8
            self.__selected_track.mixer_device.volume.value = calc_new_parm(self.__selected_track.mixer_device.volume, delta)

    def __do_cue(self, value, push_down):
        delta = push_down and value or value * 8
        self.__song.master_track.mixer_device.cue_volume.value = calc_new_parm(self.__song.master_track.mixer_device.cue_volume, delta)

    def __do_master(self, value, push_down):
        delta = push_down and value or value * 8
        self.__song.master_track.mixer_device.volume.value = calc_new_parm(self.__song.master_track.mixer_device.volume, delta)

    def __do_tempo(self, value, push_down):
        if push_down:
            self.__song.tempo = max(20, min(999, self.__song.tempo + value * 0.1))
        else:
            self.__song.tempo = max(20, min(999, self.__song.tempo + value))

    def handle_encoder(self, value, push_down):
        self._encoder_action(value, push_down)

    @property
    def mode(self):
        return self.__mode
