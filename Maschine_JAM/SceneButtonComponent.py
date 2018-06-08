# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\SceneButtonComponent.py
# Compiled at: 2018-03-21 20:20:59
from _Framework.SubjectSlot import subject_slot
from _Framework.CompoundComponent import CompoundComponent
from _Framework.InputControlElement import MIDI_NOTE_TYPE
from PadColorButton import IndexedButton
from ModifierComponent import MASK_CLEAR, MASK_SHIFT, MASK_SPEC, MASK_DUPLICATE
from JamButtonMatrix import IndexButtonMatrix
from MidiMap import COLOR_BLACK, CI_OFF, toHSB, colorOnOff, vindexof

def has_active_clips(scene):
    slots = scene.clip_slots
    for slot in slots:
        if slot.is_playing or slot.is_recording:
            return True

    return False


class SceneButtonComponent(CompoundComponent):
    __session = None
    __modifier = None
    __follow_pos = None
    __page_offset = 0
    __page_select = False

    def __init__(self, session, *a, **k):
        super(SceneButtonComponent, self).__init__(*a, **k)
        self._buttons = [ self.create_encoders(index) for index in range(8) ]
        self._bmatrix = IndexButtonMatrix(0, name='Scene_Launch_Button_Matrix')
        self._bmatrix.add_row(tuple(self._buttons))
        self._update_listener = None
        self._step_segments = None
        self._last_step_pos = 0
        self.__session = session
        self.__page_control = None
        self.__button_action = self._scene_action
        self.scenes_changed.subject = self.song()
        return

    def create_encoders(self, index):
        button = IndexedButton(False, MIDI_NOTE_TYPE, index, 1, (COLOR_BLACK, COLOR_BLACK))
        button.index = index
        button.scene = None
        button.send_index(0)
        button.add_value_listener(self._handle_button, True)
        button.set_resource_handler(lambda grabbed: self.update_grabbed(grabbed, button))
        return button

    def update_grabbed(self, grabbed, button):
        if not grabbed:
            button.refresh()

    def refresh_state(self):
        for button in self._buttons:
            button.refresh()

    def release_grab(self):
        if self._bmatrix.grabbed:
            self._bmatrix.resource.release_all()

    def bind_modify_component(self, modifier_component):
        self.__modifier = modifier_component

    @subject_slot('scenes')
    def scenes_changed(self):
        self._assign_button()

    def set_page_control(self, control):
        if control:
            self.__page_control = control
            self.__button_action = self._page_action
        else:
            self.__page_control = None
            self.__button_action = self._scene_action
        self.__page_offset = 0
        self.__page_select = False
        self._assign_button()
        return

    def assign(self):
        self._assign_button()

    def update_buttons(self):
        self._assign_button()

    def _update_button_color(self, button):
        button.empty = has_active_clips(button.scene)
        color = button.scene.color
        button.rgbcolor = color
        if color == 0:
            button.set_color((30, 28))
        else:
            button.set_color(toHSB(color))

    def notify_shift(self, shift_value):
        if self.__page_control:
            self.__page_select = shift_value
            self._assign_button()

    def notify_position(self, position, quantize, grid_elements=8):
        clip = self.song().view.detail_clip
        if clip == None:
            return
        page_pos = int(position / quantize / grid_elements) - self.__page_offset * 8
        if self.__page_select:
            pass
        else:
            if self.__follow_pos != page_pos:
                if self.__follow_pos >= 0:
                    last_button = self._buttons[self.__follow_pos]
                    last_button.send_index(last_button.prev_index)
                if page_pos in range(0, 8):
                    button = self._buttons[page_pos]
                    button.prev_index = button._last_index
                    button.send_index(2)
                    self.__follow_pos = page_pos
        return

    def _assign_button(self):
        if self.__page_control:
            clip = self.__page_control.get_clip()
            color = (4, 6)
            if clip:
                color = toHSB(clip.color)
            if self.__page_select:
                quant, clip_len, grids = self.__page_control.get_grid_info()
                pages = clip_len / quant / grids / 8
                pv = int(pages) + (pages - int(pages) > 0 and 1 or 0)
                for button in self._buttons:
                    button.scene = None
                    index = button.index
                    if index < pv:
                        button.set_color((126, 124))
                        button.send_index(index != self.__page_offset and 1 or 0)
                        button.page_off = button.index
                    else:
                        button.set_color((COLOR_BLACK, COLOR_BLACK))
                        button.send_index(0)
                        button.page_off = None

            else:
                pos, pages = self.__page_control.page_index()
                rpos = pos % 8
                offset = self.__page_offset * 8
                viewpages = min(8, pages - offset)
                self.__follow_pos = None
                for button in self._buttons:
                    button.scene = None
                    index = button.index
                    if index < viewpages:
                        button.set_color(color)
                        button.send_index(index != rpos and 1 or 0)
                        button.page = offset + index
                    else:
                        button.set_color((COLOR_BLACK, COLOR_BLACK))
                        button.send_index(0)
                        button.page = None

        else:
            for scene_index in range(8):
                scene = self.__session.scene(scene_index)
                button = self._buttons[scene_index]
                button.scene = scene._scene
                if scene._scene:
                    self._update_button_color(button)
                    button.send_index(1)
                else:
                    button.set_color(colorOnOff(CI_OFF))
                    button.send_index(0)
                    button.empty = True

        return

    def notify(self, blink_state):
        if self._bmatrix.grabbed:
            return
        if self.__page_control:
            pass
        else:
            for scene_index in range(8):
                button = self._buttons[scene_index]
                scene = button.scene
                if scene:
                    scene_active = has_active_clips(button.scene)
                    if button.rgbcolor != scene.color or button.empty != scene_active:
                        self._update_button_color(button)
                    if scene.is_triggered:
                        button.send_index(blink_state & 1 == 0 and 2 or 0)
                    elif scene_active:
                        button.send_index(0)
                    else:
                        button.send_index(1)

    def _handle_button(self, value, button):
        if value == 0 or button.grabbed:
            return
        self.__button_action(button)

    def _page_action(self, button):
        if self.__page_select:
            if button.page_off != None and button.page_off != self.__page_offset:
                self.__page_offset = button.page_off
                self.__page_control.select_pos(self.__page_offset * 8)
                self._assign_button()
        else:
            if self.__page_control and button.page != None:
                modifiers = self.__modifier.modifier_mask()
                if modifiers & MASK_CLEAR:
                    self.__page_control.clear_clip(modifiers & MASK_SHIFT != 0)
                elif modifiers & MASK_SPEC:
                    self.__page_control.repeat_section(modifiers & MASK_SHIFT != 0)
                elif modifiers & MASK_DUPLICATE:
                    self.__page_control.double_clip(modifiers & MASK_SHIFT != 0)
                else:
                    self.__page_control.select_pos(button.page)
        return

    def _scene_action(self, button):
        if button.scene:
            modifiers = self.__modifier.modifier_mask()
            if modifiers & MASK_CLEAR:
                self.delete_scene(button.scene)
            elif modifiers & MASK_DUPLICATE:
                if modifiers & MASK_SHIFT:
                    pass
                else:
                    self.duplicate_scene(button.scene)
            else:
                button.scene.fire()
        else:
            self.song().create_scene(len(self.song().scenes))

    def delete_scene(self, scene):
        song = self.song()
        sindex = vindexof(song.scenes, scene)
        if scene and len(song.scenes) > 1 and sindex >= 0:
            self.canonical_parent.show_message('Delete Scene ' + scene.name)
            song.delete_scene(sindex)

    def duplicate_scene(self, scene):
        song = self.song()
        sindex = vindexof(song.scenes, scene)
        if scene and len(song.scenes) > 1 and sindex >= 0:
            self.canonical_parent.show_message('Duplicate Scene ' + scene.name)
            song.duplicate_scene(sindex)

    def disconnect(self):
        super(SceneButtonComponent, self).disconnect()
        for button in self._buttons:
            button.unlight()
