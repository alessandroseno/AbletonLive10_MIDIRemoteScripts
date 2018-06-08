# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\MaschineMode.py
# Compiled at: 2018-03-21 20:20:59
from _Framework.CompoundComponent import CompoundComponent

class MaschineMode(CompoundComponent):
    __module__ = __name__

    def __init__(self, *a, **k):
        super(MaschineMode, self).__init__(*a, **k)
        self._active = False
        self._alternate_mode = None
        return

    def get_color(self, value, column_index, row_index):
        pass

    def notify(self, blink_state):
        pass

    def notify_mono(self, blink_state):
        pass

    def navigate(self, direction, modifier, alt_modifier=False):
        pass

    def unbind(self):
        pass

    def is_lock_mode(self):
        return True

    def enter(self):
        raise NotImplementedError, self.__class__

    def exit(self):
        raise NotImplementedError, self.__class__

    def ext_name(self):
        return 'undefined'

    def enter_edit_mode(self, action_type):
        pass

    def exit_edit_mode(self, action_type):
        pass

    def get_mode_id(self):
        return 0

    def spec_unbind(self, index=0):
        pass

    def disconnect(self):
        super(MaschineMode, self).disconnect()

    def fitting_mode(self, track):
        return self

    def device_dependent(self):
        return False

    def set_alternate_mode(self, mode):
        self._alternate_mode = mode

    def refresh(self):
        pass

    def update(self):
        pass
