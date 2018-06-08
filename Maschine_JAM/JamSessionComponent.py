# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\JamSessionComponent.py
# Compiled at: 2018-03-21 20:20:59
from MidiMap import STEP1, COLOR_BLACK, COLOR_WHITE, COLOR_WHITE_DIM, toHSB
from _Framework.SessionComponent import SessionComponent
from JamSceneComponent import JamSceneComponent
COLOR_MODE_WHITE = 1
COLOR_MODE_STD = 0

class JamSessionComponent(SessionComponent):
    """Session Component for Maschine Jam"""
    __module__ = __name__
    __matrix = None
    __matrix_lookup = []
    scene_component_type = JamSceneComponent
    _track_offset_listener = None
    _advance = STEP1
    __color_mode = COLOR_MODE_STD

    def __init__(self, *a, **k):
        super(JamSessionComponent, self).__init__(8, 8, *a, **k)
        self.__to_std_cmode()

    def _allow_updates(self):
        return True

    def set_color_mode(self, mode=None):
        if mode == None:
            if self.__color_mode == COLOR_MODE_STD:
                self.__to_white_cmode()
            else:
                self.__to_std_cmode()
        else:
            if mode == COLOR_MODE_STD:
                self.__to_std_cmode()
            else:
                self.__to_white_cmode()
        return

    def __to_std_cmode(self):
        self.get_color = self.__color_cmode
        self.notify = self.__notify_cmode_std
        self.__color_mode = COLOR_MODE_STD

    def __to_white_cmode(self):
        self.get_color = self.__color_wht_mode
        self.notify = self.__notify_cmode_wht
        self.__color_mode = COLOR_MODE_WHITE

    def get_color_mode(self):
        return self.__color_mode

    def set_matrix(self, matrix, matrix_lookup):
        self.__matrix = matrix
        self.__matrix_lookup = matrix_lookup

    def bank_down(self, amount=1):
        if self.is_enabled():
            newoff = max(0, self._scene_offset - amount)
            self.set_offsets(self._track_offset, newoff)

    def bank_up(self, amount=1):
        if self.is_enabled():
            self.set_offsets(self._track_offset, self._scene_offset + amount)

    def set_offsets(self, track_offset, scene_offset):
        if self.__matrix:
            self.__matrix.prepare_update()
        prevoffset = self._track_offset
        super(JamSessionComponent, self).set_offsets(track_offset, scene_offset)
        if prevoffset != self._track_offset and self._track_offset_listener:
            self._track_offset_listener(self._track_offset)
        if self.__matrix:
            self.__matrix.commit_update()

    def bank_left(self, amount=1):
        if self.is_enabled():
            self.set_offsets(max(0, self._track_offset - amount), self._scene_offset)

    def bank_right(self, amount=1):
        if self.is_enabled():
            self.set_offsets(self._track_offset + amount, self._scene_offset)

    def set_track_offset_listener(self, listener):
        self._track_offset_listener = listener

    def __color_cmode(self, clip_slot):
        if clip_slot == None:
            return COLOR_BLACK
        oncolor, offcolor = self.get_color_cmode_base(clip_slot)
        if clip_slot.has_clip:
            if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                return oncolor
            if clip_slot.clip.is_triggered:
                return oncolor
            if clip_slot.clip.is_playing:
                return oncolor
            return offcolor
        else:
            if clip_slot.will_record_on_start:
                return oncolor
            if clip_slot.is_playing:
                return COLOR_WHITE
            if clip_slot.controls_other_clips:
                return COLOR_WHITE_DIM
            if clip_slot.is_triggered:
                return COLOR_WHITE_DIM
        return COLOR_BLACK

    def __color_wht_mode(self, clip_slot):
        if clip_slot == None:
            return COLOR_BLACK
        oncolor, _ = self.get_color_cmode_base(clip_slot)
        if clip_slot.has_clip:
            if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                return COLOR_WHITE
            if clip_slot.clip.is_triggered:
                return COLOR_WHITE
            if clip_slot.clip.is_playing:
                return COLOR_WHITE
            return oncolor
        else:
            if clip_slot.will_record_on_start:
                return oncolor
            if clip_slot.is_playing:
                return COLOR_WHITE
            if clip_slot.controls_other_clips:
                return COLOR_WHITE_DIM
            if clip_slot.is_triggered:
                return COLOR_WHITE_DIM
        return COLOR_BLACK

    def __notify_cmode_wht(self, blink):
        sblink = blink / 2
        for scene_index in range(8):
            scene = self.scene(scene_index)
            for track_index in range(8):
                clip_slot = scene.clip_slot(track_index)._clip_slot
                if clip_slot:
                    button = self.__matrix_lookup[scene_index][track_index]
                    if clip_slot.has_clip:
                        if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                            oncolor, _ = self.get_color_cmode_base(clip_slot)
                            button.send_color_direct(sblink == 0 and oncolor or 7)
                        elif clip_slot.clip.is_triggered:
                            oncolor, _ = self.get_color_cmode_base(clip_slot)
                            button.send_color_direct(sblink == 0 and oncolor or COLOR_WHITE - 1)
                        elif clip_slot.clip.is_playing:
                            pass
                    elif clip_slot.will_record_on_start:
                        button.send_color_direct(sblink == 0 and 4 or 0)
                    elif clip_slot.is_playing:
                        button.send_color_direct(COLOR_WHITE)
                    elif clip_slot.is_triggered:
                        button.send_color_direct(sblink == 0 and COLOR_WHITE or COLOR_WHITE_DIM)
                    elif clip_slot.controls_other_clips:
                        button.send_color_direct(COLOR_WHITE_DIM)

    def __notify_cmode_std(self, blink):
        sblink = blink / 2
        for scene_index in range(8):
            scene = self.scene(scene_index)
            for track_index in range(8):
                clip_slot = scene.clip_slot(track_index)._clip_slot
                if clip_slot:
                    button = self.__matrix_lookup[scene_index][track_index]
                    if clip_slot.has_clip:
                        if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                            oncolor, _ = self.get_color_cmode_base(clip_slot)
                            button.send_color_direct(sblink == 0 and oncolor or 7)
                        elif clip_slot.clip.is_triggered:
                            oncolor, offcolor = self.get_color_cmode_base(clip_slot)
                            button.send_color_direct(sblink == 0 and oncolor or offcolor)
                        elif clip_slot.clip.is_playing:
                            pass
                    elif clip_slot.will_record_on_start:
                        button.send_color_direct(sblink == 0 and 4 or 0)
                    elif clip_slot.is_playing:
                        button.send_color_direct(COLOR_WHITE)
                    elif clip_slot.is_triggered:
                        button.send_color_direct(sblink == 0 and COLOR_WHITE or COLOR_WHITE_DIM)
                    elif clip_slot.controls_other_clips:
                        button.send_color_direct(COLOR_WHITE_DIM)

    def get_color_cmode_base(self, clip_slot):
        if clip_slot != None:
            if clip_slot.has_clip:
                color = toHSB(clip_slot.clip.color)
                return color
            if clip_slot.controls_other_clips:
                pass
        return (0, 0)

    def disconnect(self):
        super(JamSessionComponent, self).disconnect()
