# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\Encoder.py
# Compiled at: 2017-09-17 14:40:56
import Live
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE
from _Framework.SubjectSlot import subject_slot
from MidiMap import debug_out

class Encoder(SliderElement):
    """ Class representing a slider on the controller """

    def __init__(self, msg_type, channel, identifier, index, handler, *a, **k):
        assert msg_type is not MIDI_NOTE_TYPE
        super(Encoder, self).__init__(msg_type, channel, identifier, *a, **k)
        self.__grabbed = False
        self.__buffered_value = None
        self.__led_value = None
        self.__index = index
        self.__cfg = (0, 0)
        self.__cfg_over = (0, 2)
        return

    @property
    def is_grabbed(self):
        return self.__grabbed

    @property
    def led_value(self):
        return self.__led_value

    @led_value.setter
    def led_value(self, value):
        self.__led_value = value

    def _set_cfg(self, mode, color):
        self.__cfg = (
         mode, color)

    def set_cfg(self, mode, color):
        self.__cfg_over = (
         mode, color)

    def get_strip_cfg(self):
        if self.is_grabbed:
            return self.__cfg_over
        return self.__cfg

    def set_display_value(self, value, force=False, channel=None):
        self.__buffered_value = value
        if not self.__grabbed:
            super(Encoder, self).send_value(value, force, channel)

    def send_value(self, value, force=False, channel=None):
        super(Encoder, self).send_value(value, True, channel)

    def grab_control(self):
        self.__grabbed = True
        super(Encoder, self).send_value(0, True)

    def release_control(self):
        self.__grabbed = False
        self.set_display_value(self.__buffered_value or 0, True)


class GrabEncoder(SliderElement):
    """ Class representing Stateless Encoder that can be grabbed """

    def __init__(self, msg_type, channel, identifier, *a, **k):
        assert msg_type is not MIDI_NOTE_TYPE
        super(GrabEncoder, self).__init__(msg_type, channel, identifier, *a, **k)
        self.__grabbed = False

    @property
    def is_grabbed(self):
        return self.__grabbed

    def grab_control(self):
        self.__grabbed = True

    def release_control(self):
        self.__grabbed = False
