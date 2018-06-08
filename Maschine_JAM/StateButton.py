# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\StateButton.py
# Compiled at: 2018-03-20 21:29:04
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE

class StateButton(ButtonElement):
    """ Special button class that can be configured with custom on- and off-values """
    __module__ = __name__

    def __init__(self, is_momentary, msg_type, channel, identifier, *a, **k):
        ButtonElement.__init__(self, is_momentary, msg_type, channel, identifier, *a, **k)
        self._is_enabled = True
        self._is_notifying = False
        self._force_next_value = False
        self._last_value = 0
        self.__main_listener = None
        self.__grabbed = False
        self.__buffered_value = None
        self.resource.on_received = self.grab_control
        self.resource.on_lost = self.release_control
        return

    def turn_off(self):
        self._last_value = 0
        self.set_display_value(0, True)

    def turn_on(self):
        self._last_value = 127
        self.set_display_value(127, True)

    @property
    def grabbed(self):
        return self.__grabbed

    def set_value(self, value):
        if value != self._last_value:
            self._last_value = value
            self.set_display_value(value, True)

    def set_enabled(self, enabled):
        self._is_enabled = enabled

    def send_value(self, value, force=False, channel=None):
        super(StateButton, self).send_value(value, True)

    def reset(self):
        self._last_value = 0
        self.send_value(0, True)

    def set_display_value(self, value, force=False, channel=None):
        self.__buffered_value = value
        if not self.__grabbed:
            self.send_value(value, force, channel)

    def grab_control(self, client):
        self.__grabbed = True
        self.notify_ownership_change(client, True)

    def release_control(self, client):
        self.__grabbed = False
        self.notify_ownership_change(client, False)
        if self.__buffered_value >= 0:
            self.send_value(self.__buffered_value, True)

    def remove_value_listener(self, *a, **k):
        super(self.__class__, self).remove_value_listener(*a, **k)
        if self.grabbed:
            self.resource.release_all()

    def install_connections(self, install_translation_callback, install_mapping_callback, install_forwarding_callback):
        if self._is_enabled:
            ButtonElement.install_connections(self, install_translation_callback, install_mapping_callback, install_forwarding_callback)
        else:
            if self._msg_channel != self._original_channel or self._msg_identifier != self._original_identifier:
                install_translation_callback(self._msg_type, self._original_identifier, self._original_channel, self._msg_identifier, self._msg_channel)


class SysExButton(ButtonElement):
    """Button that represents Shift Status """
    __module__ = __name__

    def __init__(self, identifier, *a, **k):
        ButtonElement.__init__(self, True, MIDI_CC_TYPE, 15, identifier, *a, **k)
        self.__main_listener = None
        self.__grabbed = False
        self.__buffered_value = None
        return

    @property
    def is_grabbed(self):
        return self.__grabbed

    def send_value(self, value, opt_value=None):
        pass

    def send_value_ext(self, value, force=False, channel=None):
        pass

    def grab_control(self):
        self.__grabbed = True

    def release_control(self):
        self.__grabbed = False


class TouchButton(ButtonElement):
    """ Touch """
    __module__ = __name__

    def __init__(self, msg_type, channel, identifier, *a, **k):
        ButtonElement.__init__(self, True, msg_type, channel, identifier, *a, **k)
        self.__grabbed = False
        self.__main_listener = None
        self.resource.on_received = self.grab_control
        self.resource.on_lost = self.release_control
        return

    @property
    def is_grabbed(self):
        return self.__grabbed

    def grab_control(self, client):
        self.__grabbed = True
        if self.__main_listener:
            super(TouchButton, self).remove_value_listener(self.__main_listener)

    def release_control(self, client):
        self.__grabbed = False
        if self.__main_listener:
            super(TouchButton, self).add_value_listener(self.__main_listener)

    def add_value_listener(self, *a, **k):
        if not self.__main_listener:
            self.__main_listener = a[0]
        super(TouchButton, self).add_value_listener(*a, **k)
