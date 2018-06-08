# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\MaschineButtonMatrix.py
# Compiled at: 2017-08-10 18:34:01
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.CompoundElement import CompoundElement
from _Framework.Util import in_range
from MidiMap import *

class MaschineButtonMatrix(ButtonMatrixElement):

    def __init__(self, index_offset, rows=[], *a, **k):
        super(MaschineButtonMatrix, self).__init__(*a, **k)
        self._grabbed = False
        self.__index_offset = index_offset
        self._pending_grab = False
        self._listern_stack = None
        self._value_listener_action = None
        self._external_unbind_lister = None
        self.__batch_updater = None
        return

    def prepare_update(self):
        pass

    def commit_update(self):
        pass

    def set_user_unbind_listener(self, listener):
        self._external_unbind_lister = listener

    def register_batch_updater(self, updater):
        self.__batch_updater = updater

    def add_value_listener(self, *a, **k):
        if len(a) == 0:
            return
        self._value_listener_action = a[0]
        if self._grabbed:
            super(MaschineButtonMatrix, self).add_value_listener(*a, **k)
            self._pending_grab = False

    def unbind_value_listener(self):
        if self._value_listener_action:
            super(MaschineButtonMatrix, self).remove_value_listener(self._value_listener_action)

    def remove_value_listener(self, *a, **k):
        super(MaschineButtonMatrix, self).remove_value_listener(*a, **k)
        if self._external_unbind_lister:
            self._external_unbind_lister.handle_user_mode_removed()

    def update_all(self, data):
        if not self._grabbed:
            return
        self.prepare_update()
        for button, (col, row) in self.iterbuttons():
            idx = row * 4 + col
            if idx < len(data) and button and data[idx] in range(128):
                button.send_color_direct(data[idx])

        self.commit_update()

    def switch_to_user_action(self):
        if self._value_listener_action:
            super(MaschineButtonMatrix, self).add_value_listener(self._value_listener_action)
            self._grabbed = True
        else:
            self._pending_grab = True
            self._grabbed = True

    def exit_user_action(self):
        self.unbind_value_listener()
        self._grabbed = False
        self._pending_grab = False

    def grabresource(self, val):
        self._grabbed = val
        if not val:
            self._pending_grab = False

    @property
    def grabbed(self):
        return self._grabbed

    @property
    def index_offset(self):
        return self.__index_offset

    def send_value(self, column, row, value, force=False):
        if self.grabbed:
            assert in_range(value, 0, 128)
            assert in_range(column, 0, self.width())
            assert in_range(row, 0, self.height())
            if len(self._buttons[row]) > column:
                button = self._buttons[row][column]
                if button:
                    if value == 0:
                        button.send_color_direct(0)
                    else:
                        button.send_color_direct(value)


class IndexButtonMatrix(ButtonMatrixElement):

    def __init__(self, index_offset, rows=[], *a, **k):
        super(IndexButtonMatrix, self).__init__(*a, **k)
        self.__grabbed = False
        self.__batch_updater = None
        self.__index_offset = index_offset
        return

    def register_batch_updater(self, updater):
        self.__batch_updater = updater

    def grab_control(self):
        self.__grabbed = True
        for button, (_, _) in self.iterbuttons():
            if button:
                button.unlight(True)
                button.update_grab(True)

    def release_control(self):
        self.__grabbed = False
        for button, (_, _) in self.iterbuttons():
            if button:
                button.set_to_black()
                button.update_grab(False)

    def update_all(self, data):
        if not self.__grabbed:
            return
        for button, (col, row) in self.iterbuttons():
            idx = row * 4 + col
            if idx < len(data) and button and data[idx] in range(128):
                button.send_color(data[idx], True)

    @property
    def index_offset(self):
        return self.__index_offset

    @property
    def grabbed(self):
        return self.__grabbed

    def send_value(self, column, row, value, force=False):
        if self.__grabbed:
            assert in_range(value, 0, 128)
            assert in_range(column, 0, self.width())
            assert in_range(row, 0, self.height())
            if len(self._buttons[row]) > column:
                button = self._buttons[row][column]
                if button:
                    button.send_color(value)
