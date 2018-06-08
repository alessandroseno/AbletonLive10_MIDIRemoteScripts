# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\TouchStripSlider.py
# Compiled at: 2018-03-20 21:29:04
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE

class TouchStripSlider(SliderElement):
    """ Class representing a slider on the controller """

    def __init__(self, msg_type, channel, identifier, index, handler, *a, **k):
        assert msg_type is not MIDI_NOTE_TYPE
        super(TouchStripSlider, self).__init__(msg_type, channel, identifier, *a, **k)
        self.__grabbed = False
        self.__buffered_value = None
        self.__led_value = None
        self.__index = index
        self.__cfg = (0, 0)
        self.__cfg_over = (0, 2)
        self.__sysexhandler = handler
        self.resource.on_received = self.grab_control
        self.resource.on_lost = self.release_control
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
        if self.__grabbed:
            self.__sysexhandler.update_bar_config()

    def get_strip_cfg(self):
        if self.is_grabbed:
            return self.__cfg_over
        return self.__cfg

    def remove_value_listener(self, *a, **k):
        super(self.__class__, self).remove_value_listener(*a, **k)
        if self.is_grabbed:
            self.resource.release_all()

    def set_display_value(self, value, force=False, channel=None):
        self.__buffered_value = value
        if not self.__grabbed:
            super(TouchStripSlider, self).send_value(value, force, channel)

    def send_value(self, value, force=False, channel=None):
        super(TouchStripSlider, self).send_value(value, True, channel)

    def grab_control(self, client):
        self.__grabbed = True
        self.__sysexhandler.update_bar_config()
        super(TouchStripSlider, self).send_value(0, True)

    def release_control(self, client):
        self.__grabbed = False
        self.__sysexhandler.reset_led()
        self.__sysexhandler.set_led_value(self.__index, self.__led_value or 0)
        self.__sysexhandler.update_led()
        self.__sysexhandler.update_bar_config()
        self.set_display_value(self.__buffered_value or 0, True)


class GrabEncoder(SliderElement):
    """ Class representing Stateless Encoder that can be grabbed """

    def __init__(self, msg_type, channel, identifier, *a, **k):
        assert msg_type is not MIDI_NOTE_TYPE
        super(GrabEncoder, self).__init__(msg_type, channel, identifier, *a, **k)
        self.__grabbed = False
        self.resource.on_received = self.grab_control
        self.resource.on_lost = self.release_control

    @property
    def is_grabbed(self):
        return self.__grabbed

    def grab_control(self, client):
        self.__grabbed = True

    def release_control(self, client):
        self.__grabbed = False

    def remove_value_listener(self, *a, **k):
        super(self.__class__, self).remove_value_listener(*a, **k)
        if self.__grabbed:
            self.resource.release_all()
