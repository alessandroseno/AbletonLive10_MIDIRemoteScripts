# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\JamButtonMatrix.py
# Compiled at: 2018-03-21 20:20:59
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.Util import in_range

class JamButtonMatrix(ButtonMatrixElement):

    def __init__(self, index_offset, rows=[], *a, **k):
        super(JamButtonMatrix, self).__init__(*a, **k)
        self._grabbed = False
        self.__index_offset = index_offset
        self._listern_stack = None
        self._value_listener_action = None
        self._external_unbind_lister = None
        self.__batch_updater = None
        self.resource.on_received = self.__on_received
        self.resource.on_lost = self.__on_lost
        return

    def __on_received(self, client, **k):
        self.switch_to_user_action()
        self.canonical_parent._main_mode_container.enter_user_mode()

    def __on_lost(self, client):
        self.exit_user_action()
        self.canonical_parent._main_mode_container.exit_user_mode()

    def on_nested_control_element_lost(self, control):
        pass

    def switch_to_user_action(self):
        if self._value_listener_action:
            super(JamButtonMatrix, self).add_value_listener(self._value_listener_action)
            self._grabbed = True
        else:
            self._grabbed = True

    def exit_user_action(self):
        self._grabbed = False

    def set_user_unbind_listener(self, listener):
        self._external_unbind_lister = listener

    def register_batch_updater(self, updater):
        self.__batch_updater = updater

    def prepare_update(self):
        for button, (_, _) in self.iterbuttons():
            if button:
                button.disable_cc_midi()

    def commit_update(self):
        if self.__batch_updater:
            self.__batch_updater.update_all()
        for button, (_, _) in self.iterbuttons():
            if button:
                button.enable_cc_midi()

    def remove_value_listener(self, *a, **k):
        super(JamButtonMatrix, self).remove_value_listener(*a, **k)
        if self._external_unbind_lister:
            self._external_unbind_lister.handle_user_mode_removed()

    def update_all(self, data):
        if not self._grabbed:
            return
        self.prepare_update()
        for button, (col, row) in self.iterbuttons():
            idx = row * 8 + col
            if idx < len(data) and button and data[idx] in range(128):
                button.send_color_direct(data[idx])

        self.commit_update()

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
        self.resource.on_received = self.__on_received
        self.resource.on_lost = self.__on_lost
        return

    def __on_received(self, client):
        self.notify_ownership_change(client, True)
        self.grab_control()

    def __on_lost(self, client):
        self.release_control()
        self.notify_ownership_change(client, False)

    def on_nested_control_element_lost(self, control):
        pass

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
            idx = row * 8 + col
            if idx < len(data) and button and data[idx] in range(128):
                button.send_color(data[idx], True)

    def remove_value_listener(self, *a, **k):
        super(IndexButtonMatrix, self).remove_value_listener(*a, **k)
        if self.__grabbed:
            self.resource.release_all()

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


class MatrixState:

    def __init__(self, parent):
        self.__cfg_msg = [
         240, 0, 33, 9, 21, 0, 77, 80, 0, 1, 2]
        for _ in range(80):
            self.__cfg_msg.append(0)

        self.__cfg_msg.append(247)
        self.__parent = parent
        self.__controls = []

    def register_matrix(self, bmatrix):
        self.__controls.append(bmatrix)
        self.__controls.sort(key=lambda c: c.index_offset)
        bmatrix.register_batch_updater(self)

    def update_all(self):
        self.refresh_state()
        self.__parent._send_midi(tuple(self.__cfg_msg))

    def refresh_state(self):
        for bmatrix in self.__controls:
            for button, (col, row) in bmatrix.iterbuttons():
                if button:
                    index = bmatrix.index_offset + row * 8 + col
                    self.__cfg_msg[index + 11] = button.color_value()

    def update_all_values(self, data):
        self.refresh_state()
        for c in self.__controls:
            for button, (col, row) in c.iterbuttons():
                if button:
                    index = row * 8 + col + c.index_offset
                    if index < len(data):
                        color = data[index]
                        self.__cfg_msg[index + 11] = color
                        button.set_color_value(color)
                    else:
                        self.__cfg_msg[index + 11] = 0
                        button.set_color_value(0)

        self.send_update()

    def update_values(self, control, data):
        self.refresh_state()
        for button, (col, row) in control.iterbuttons():
            if button:
                index = row * 8 + col
                if index < len(data):
                    color = data[index]
                    self.__cfg_msg[index + control.index_offset + 11] = color
                    button.set_color_value(color)
                else:
                    self.__cfg_msg[index + control.index_offset + 11] = 0
                    button.set_color_value(0)

        self.send_update()

    def send_update(self):
        self.__parent._send_midi(tuple(self.__cfg_msg))
