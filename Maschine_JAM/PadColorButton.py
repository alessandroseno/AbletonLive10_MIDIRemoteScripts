# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\PadColorButton.py
# Compiled at: 2018-03-20 21:29:04
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import InputControlElement, MIDI_NOTE_TYPE, MIDI_NOTE_ON_STATUS
from MidiMap import MATRIX_NOTE_NR, NON_FEEDBACK_CHANNEL, COLOR_BLACK

class PadColorButton(ButtonElement):
    """ Colored Maschine Pads """
    __module__ = __name__

    def __init__(self, is_momentary, channel, row_index, column_index, color_source):
        ButtonElement.__init__(self, is_momentary, MIDI_NOTE_TYPE, channel, MATRIX_NOTE_NR + row_index * 8 + column_index)
        self._is_enabled = True
        self._color_source = color_source
        self._row_index = row_index
        self._column_index = column_index
        self.last_value = None
        self.set_channel(NON_FEEDBACK_CHANNEL)
        self.state = 0
        self.__cc_enabled = True
        return

    def infox(self):
        return 'PC R=' + str(self._row_index) + ' C=' + str(self._column_index)

    def enable_cc_midi(self):
        self.__cc_enabled = True

    def disable_cc_midi(self):
        self.__cc_enabled = False

    def get_identifier(self):
        return self._msg_identifier

    def get_position(self):
        return (
         self._column_index, self._row_index)

    def reset(self):
        self.last_value = None
        return

    def turn_off(self):
        self.last_value = COLOR_BLACK
        if self.__cc_enabled:
            self.send_midi((MIDI_NOTE_ON_STATUS, self._original_identifier, COLOR_BLACK))

    def turn_on(self):
        self.send_value(1, True)

    def refresh(self):
        self.send_value(self.last_value, True)

    def set_send_note(self, note):
        if note in range(128):
            self._msg_identifier = note
            if not self._is_enabled:
                self.canonical_parent._translate_message(self._msg_type, self._original_identifier, self._original_channel, note, self._msg_channel)

    def set_to_notemode(self, notemode):
        if self._is_enabled != notemode:
            return
        self._is_enabled = not notemode
        if notemode:
            self.set_channel(0)
            self._is_being_forwarded = False
            self.suppress_script_forwarding = True
        else:
            self.set_channel(NON_FEEDBACK_CHANNEL)
            self._is_being_forwarded = True
            self.suppress_script_forwarding = False
            self._msg_identifier = self._original_identifier

    def send_value(self, value, force_send=False):
        if force_send or self._is_being_forwarded:
            self.send_color(value)

    def send_color(self, value):
        color = self._color_source.get_color(value, self._column_index, self._row_index)
        if color != self.last_value:
            self.last_value = color
            if self.__cc_enabled:
                if color is None:
                    self.send_midi((MIDI_NOTE_ON_STATUS, self._original_identifier, COLOR_BLACK))
                else:
                    self.send_midi((MIDI_NOTE_ON_STATUS, self._original_identifier, color))
        return

    def send_color_direct(self, color):
        self.last_value = color
        if self.__cc_enabled:
            if color is None:
                self.send_midi((MIDI_NOTE_ON_STATUS, self._original_identifier, COLOR_BLACK))
            else:
                self.send_midi((MIDI_NOTE_ON_STATUS, self._original_identifier, color))
        return

    def brighten(self, sat, bright):
        pass

    def switch_off(self):
        self.last_value = COLOR_BLACK
        if self.__cc_enabled:
            self.send_midi((MIDI_NOTE_ON_STATUS, self._original_identifier, COLOR_BLACK))

    def color_value(self):
        return self.last_value or 0

    def set_color_value(self, color):
        self.last_value = color

    def disconnect(self):
        ButtonElement.disconnect(self)
        self._is_enabled = None
        self._color_source = None
        self._report_input = None
        self._column_index = None
        self._row_index = None
        return


class IndexedButton(ButtonElement):
    """ Special button class that has on, off, color an can also be a None Color Button """
    __module__ = __name__

    def __init__(self, is_momentary, midi_type, identifier, channel, color_list):
        ButtonElement.__init__(self, is_momentary, midi_type, channel, identifier)
        self._msg_identifier = identifier
        self._color_list = color_list
        self._last_color = None
        self._last_index = 0
        self._midi_type = midi_type
        self.__note_on_code = MIDI_NOTE_ON_STATUS | channel
        self.__grabbed = False
        self.__resource_hander = None
        return

    @property
    def grabbed(self):
        return self.__grabbed

    def __send_midi(self, color):
        if not self.grabbed:
            self.send_midi((self.__note_on_code, self._original_identifier, color))

    def send_index(self, index):
        if self._color_list == None:
            self._last_color = COLOR_BLACK
            self.__send_midi(COLOR_BLACK)
        else:
            if index < len(self._color_list):
                if self._color_list[index] != self._last_color:
                    self._last_color = self._color_list[index]
                    self.__send_midi(self._last_color)
            else:
                icolor = self._color_list[0] + 1
                if icolor != self._last_color:
                    self._last_color = icolor
                    self.__send_midi(self._last_color)
        self._last_index = index
        return

    def set_resource_handler(self, handler):
        self.__resource_hander = handler

    def set_color(self, color_list):
        self._color_list = color_list
        if not self.__grabbed:
            self.update()

    def reset(self):
        self._last_color = None
        self._last_index = 0
        return

    def update_grab(self, grabbed):
        self.__grabbed = grabbed
        if self.__resource_hander:
            self.__resource_hander(self.__grabbed)

    def send_color(self, color, force=True):
        if color != self._last_color or force:
            self.send_midi((self.__note_on_code, self._original_identifier, color))
            self._last_color = color

    def color_value(self):
        return self._last_color or 0

    def set_color_value(self, color):
        self._last_color = color

    def refresh(self):
        self.send_midi((self.__note_on_code, self._original_identifier, self._last_color))

    def update(self):
        if self._last_index >= len(self._color_list):
            self._last_index = 0
        self.send_index(self._last_index)

    def set_to_black(self):
        self._last_color = COLOR_BLACK

    def unlight(self, force=False):
        if force or self._last_color != COLOR_BLACK:
            self._last_color = COLOR_BLACK
            self.send_midi((self.__note_on_code, self._original_identifier, COLOR_BLACK))

    def turn_on(self):
        self.send_index(1)

    def turn_off(self):
        self.send_index(0)

    def disconnect(self):
        InputControlElement.disconnect(self)
