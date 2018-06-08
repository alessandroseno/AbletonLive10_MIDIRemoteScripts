# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\SessionMode.py
# Compiled at: 2017-08-10 18:34:01
from MaschineMode import MaschineMode
from Constants import CLIP_MODE, NAV_SRC_BUTTON
from MidiMap import *

class SessionMode(MaschineMode):
    __module__ = __name__

    def __init__(self, *a, **k):
        super(SessionMode, self).__init__(*a, **k)

    def ext_name(self):
        return 'session_mode'

    def get_color(self, value, column_index, row_index):
        session = self.canonical_parent.get_session()
        scene = session.scene(row_index)
        clip_slot = scene.clip_slot(column_index)._clip_slot
        color = session.get_color(clip_slot)
        return color

    def handle_edit(self, clipslot):
        debug_out(' edit modifier ' + str(clipslot.get_index()) + ' ')

    def notify(self, blink_state):
        self.canonical_parent.get_session().notify(blink_state)

    def enter_edit_mode(self, mode_type):
        self.canonical_parent.get_session().set_enabled(False)

    def exit_edit_mode(self, mode_type):
        self.canonical_parent.get_session().set_enabled(True)

    def get_mode_id(self):
        return CLIP_MODE

    def navigate(self, nav_dir, modifier, alt_modifier=False, nav_source=NAV_SRC_BUTTON):
        if modifier:
            if nav_dir == 1:
                self.canonical_parent.get_session().bank_up(alt_modifier and 4 or 1)
            else:
                self.canonical_parent.get_session().bank_down(alt_modifier and 4 or 1)
        else:
            if nav_dir == 1:
                self.canonical_parent.get_session().bank_right(alt_modifier and 4 or 1)
            else:
                self.canonical_parent.get_session().bank_left(alt_modifier and 4 or 1)

    def enter(self):
        self._active = True
        matrix = self.canonical_parent.get_button_matrix()
        matrix.prepare_update()
        for button, (column, row) in matrix.iterbuttons():
            if button:
                button.set_to_notemode(False)
                scene = self.canonical_parent.get_session().scene(row)
                clip_slot = scene.clip_slot(column)
                clip_slot.set_launch_button(button)

        matrix.commit_update()

    def refresh(self):
        matrix = self.canonical_parent.get_button_matrix()
        matrix.prepare_update()
        if self._active:
            for button, (_, _) in matrix.iterbuttons():
                if button:
                    button.reset()
                    button.refresh()

        matrix.commit_update()

    def exit(self):
        self._active = False
        self.canonical_parent.deassign_matrix()
        self.canonical_parent.get_session().set_clip_launch_buttons(None)
        return
