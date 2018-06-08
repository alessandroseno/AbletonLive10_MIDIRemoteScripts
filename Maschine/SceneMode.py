# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\SceneMode.py
# Compiled at: 2016-02-05 11:51:57
import Live
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.ButtonElement import *
from MIDI_Map import *
from MaschineMode import MaschineMode

def play_count(scene):
    clip_slots = scene.clip_slots
    count = 0
    playcount = 0
    for cs_index in range(len(clip_slots)):
        clip_slot = clip_slots[cs_index]
        if clip_slot.has_clip:
            count = count + 1
            if clip_slot.clip.is_playing:
                playcount = playcount + 1

    return (
     count, playcount)


class SceneElement:

    def __init__(self, index, mode, *a, **k):
        if not isinstance(mode, SceneMode):
            raise AssertionError
        self._button = None
        self._index = index
        self._scene = None
        self._mode = mode
        self.blinking = False
        self.active = False
        return

    def release(self):
        if self._button != None:
            self._button.remove_value_listener(self._launch_value)
            self._scene = None
            self.active = False
            self._button = None
        return

    def set_button(self, button, scene, index):
        assert button == None or isinstance(button, ButtonElement)
        assert scene == None or isinstance(scene, Live.Scene.Scene)
        self._scene = scene
        self._index = index
        if button != self._button:
            if self._button != None:
                self._button.remove_value_listener(self._launch_value)
            self._button = button
            if self._button != None:
                self._button.add_value_listener(self._launch_value)
        return

    def _launch_value(self, value):
        if self._mode._editmode.hasModification(SCENE_MODE):
            if value > 0:
                self._mode._editmode.edit_scene_slot(self._scene, self._index)
        else:
            if value > 0 and self._scene != None:
                self._scene.fire()
        return

    def _get_color(self):
        if self._scene == None:
            return PColor.OFF
        clip_slots = self._scene.clip_slots
        if self._scene.is_triggered:
            self.blinking = True
        else:
            self.blinking = False
        count, playcount = play_count(self._scene)
        if playcount > 0:
            self.active = True
            return PColor.SCENE_PLAYING
        self.active = False
        if count > 0:
            return PColor.SCENE_HASCLIPS
        return PColor.SCENE_NO_CLIPS
        return PColor.OFF

    def notify(self, blinking_state):
        color = self._get_color()
        if blinking_state == 0 and self.blinking:
            self._button.send_color_direct(color[0])
        else:
            if blinking_state > 0 and self.blinking:
                self._button.send_color_direct(color[1])
            else:
                if self.active:
                    self._button.send_color_direct(color[0])
                else:
                    self._button.send_color_direct(color[1])

    def _do_mono_blink_fast(self, blink_state):
        if blink_state == 0 or blink_state == 2:
            self._button.turn_on()
        else:
            self._button.turn_off()

    def _do_mono_blink_slow(self, blink_state):
        if blink_state == 0:
            self._button.turn_on()
        else:
            self._button.turn_off()

    def notify_mono(self, blink_state):
        if self._scene == None:
            self._button.turn_off()
        else:
            if self._scene.is_triggered:
                self._do_mono_blink_fast(blink_state)
            else:
                count, playcount = play_count(self._scene)
                if playcount > 0:
                    self._do_mono_blink_slow(blink_state)
                else:
                    if count > 0:
                        self._button.turn_on()
                    else:
                        self._button.turn_off()
        return


class SceneMode(MaschineMode):

    def __init__(self, button_index, *a, **k):
        super(SceneMode, self).__init__(button_index, *a, **k)
        self.elements = tuple((SceneElement(idx, self) for idx in range(16)))
        self.offset = 0
        self.song().add_scenes_listener(self._scene_changed)
        self._editmode = None
        return

    def set_edit_mode(self, editmode):
        self._editmode = editmode

    def navigate(self, dir, modifier, alt_modifier=False):
        new_offset = self.offset + dir
        if new_offset >= 0 and new_offset + 16 <= len(self.song().scenes):
            self.offset = new_offset
            self._assign_button_to_scenes()
            self.refresh()
            self.canonical_parent.show_message('Scene Mode Scenes ' + str(self.offset + 1) + ' - ' + str(self.offset + 16))

    def get_color(self, value, column, row):
        index = (3 - row) * 4 + column
        cindex = value > 0 and 1 or 0
        color = self.elements[index]._get_color()
        return color[cindex]

    def _scene_changed(self):
        if self._active:
            if self.offset + 16 > len(self.song().scenes):
                self.offset = max(0, len(self.song().scenes) - 16)
            self._assign_button_to_scenes()
            self.notify(0)

    def get_mode_id(self):
        return SCENE_MODE

    def refresh(self):
        if self._active:
            for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                if button:
                    index = (3 - row) * 4 + column
                    button.reset()
                    button.send_color_direct(self.elements[index]._get_color()[1])

    def notify(self, blink_state):
        if blink_state == 0 or blink_state == 2:
            on = blink_state == 0 and 1 or 0
            for scene_element in self.elements:
                scene_element.notify(on)

    def notify_mono(self, blink_state):
        for scene_element in self.elements:
            scene_element.notify_mono(blink_state)

    def _assign_button_to_scenes(self):
        scenes = self.song().scenes
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                index = (3 - row) * 4 + column
                sindex = index + self.offset
                if sindex < len(scenes):
                    self.elements[index].set_button(button, scenes[sindex], sindex)
                else:
                    self.elements[index].set_button(button, None, sindex)

        return

    def _assign(self):
        scenes = self.song().scenes
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                index = (3 - row) * 4 + column
                sindex = index + self.offset
                self.canonical_parent._forwarding_registry[(MIDI_NOTE_ON_STATUS, button.get_identifier())] = button
                self.canonical_parent._forwarding_registry[(MIDI_NOTE_OFF_STATUS, button.get_identifier())] = button
                button.set_to_notemode(False)
                if sindex < len(scenes):
                    self.elements[index].set_button(button, scenes[sindex], sindex)
                else:
                    self.elements[index].set_button(button, None, sindex)
                button.send_color_direct(self.elements[index]._get_color()[1])

        return

    def enter(self):
        self._active = True
        self._assign()

    def exit(self):
        self._active = False
        for scene_element in self.elements:
            if scene_element:
                scene_element.release()

    def unbind(self):
        self.song().remove_scenes_listener(self._scene_changed)
