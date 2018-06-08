# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\TrackMode.py
# Compiled at: 2017-09-17 14:33:24
import Live
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.ButtonElement import *
from _Framework.CompoundComponent import CompoundComponent
from MidiMap import debug_out, toHSB
from _Framework.SubjectSlot import subject_slot
from Constants import *
from MaschineMode import MaschineMode

class TrackHandler(CompoundComponent):
    __index = None
    __button = None
    __track = None
    __action = None
    __use_track_color = True
    __active = False

    def __init__(self, index, *a, **k):
        super(TrackHandler, self).__init__(*a, **k)
        self.__index = index

    def set_track_button(self, button):
        self.__button = button

    def release_button(self):
        self.__button = None
        return

    def set_no_track_action(self, action):
        if self.__action:
            self.__button.remove_value_listener(self.__action)
        self.__action = action
        self.__button.add_value_listener(self.__action, True)
        self.__active = True

    def assign_track(self, track):
        if self.__action:
            self.__button.remove_value_listener(self.__action)
        if track:
            self.__track = track
            self.__action = self._track_action
            self.__button.add_value_listener(self.__action, True)
            self._handle_color_changed.subject = self.__track
            self.__active = True
        else:
            self.__track = None
            self.__action = None
            self.__active = False
        return

    def unbind(self):
        if self.__action:
            self.__button.remove_value_listener(self.__action)
        if self.__track:
            self._handle_color_changed.subject = None
        self.__action = None
        self.__track = None
        self.__active = False
        return

    def _track_action(self, value, button):
        if value == 0:
            self.canonical_parent.handle_track_select(self.__track)

    def update_value(self):
        pass

    def send_color(self, value=0):
        if not self.__active:
            return
        if self.__track:
            color = toHSB(self.__track.color)
            self.__button.send_color_direct(color[self.__track != self.song().view.selected_track and 1 or 0])
        else:
            self.__button.send_color_direct(0)

    @subject_slot('color')
    def _handle_color_changed(self):
        if not self.__active:
            return
        if self.__track and self.__use_track_color:
            self.send_color()


class TrackMode(MaschineMode):
    __track_handlers = None
    __mode = SEL_MODE_SELECT

    def __init__(self, *a, **k):
        super(TrackMode, self).__init__(*a, **k)
        self.__track_handlers = [ TrackHandler(idx) for idx in range(16) ]
        self._handle_selection.subject = self.song().view
        self._tracks_change.subject = self.song()
        self._visible_changed.subject = self.song()

    @subject_slot('selected_track')
    def _handle_selection(self):
        if not self._active:
            return
        if self.__mode == SEL_MODE_SELECT:
            for i in range(8):
                self.__track_handlers[i].send_color()

    @subject_slot('tracks')
    def _tracks_change(self):
        if not self._active:
            return
        self._assign_tracks()
        self.refresh()

    @subject_slot('visible_tracks')
    def _visible_changed(self):
        if not self._active:
            return
        self._assign_tracks()
        self.refresh()

    def init_elements(self):
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                index = row * 4 + column
                self.__track_handlers[index].set_track_button(button)

    def navigate(self, direction, modifier, alt_modifier=False):
        pass

    def get_color(self, value, column, row):
        return (4, 7)[value > 0 and 1 or 0]

    def get_mode_id(self):
        return TRACK_MODE

    def refresh(self):
        if self._active:
            for handler in self.__track_handlers:
                handler.send_color()

    def notify(self, blink_state):
        if blink_state == 0 or blink_state == 2:
            pass

    def notify_mono(self, blink_state):
        pass

    def gettrack(self, index, off):
        tracks = self.song().visible_tracks
        if index + off < len(tracks):
            return tracks[index + off]
        return

    def _deassign(self):
        for handler in self.__track_handlers:
            handler.unbind()

    def _assign_tracks(self):
        trackoff = self.canonical_parent._session.track_offset()
        for i in range(16):
            handler = self.__track_handlers[i]
            handler.unbind()
            if i < 8:
                track = self.gettrack(i, trackoff)
                if track is None:
                    handler.set_no_track_action(self.empty_action)
                else:
                    handler.assign_track(track)
            else:
                handler.set_no_track_action(self._global_action)

        return

    def _global_action(self, value, button):
        if value == 0:
            return

    def empty_action(self, value, button):
        if value == 0:
            return
        if self.canonical_parent.is_shift_down():
            self.song().create_audio_track(-1)
        else:
            if self.canonical_parent.is_select_down():
                self.song().create_audio_track(-1)
            else:
                self.song().create_midi_track(-1)

    def handle_shift(self, shift_value):
        if shift_value:
            for handler in self.__track_handlers:
                handler.set_no_track_action(self.handle_shift_button)

        else:
            self._assign_tracks()

    def handle_shift_button(self, value, button):
        if value != 0:
            self.canonical_parent.handle_edit_action(button.get_position())

    def enter(self):
        self._active = True
        self._assign_tracks()
        self.refresh()

    def exit(self):
        self._active = False
        self._deassign()


class LevelTracks(CompoundComponent):
    __track = None
    __color = 0
    __index = 0
    __last_meter_val = 0
    __last_bar = (0, 0, 0, 0)

    def __init__(self, index, *a, **k):
        super(LevelTracks, self).__init__(*a, **k)
        self.__index = index
        self.__buttons = [None, None, None, None]
        return

    def set_button(self, button, index):
        self.__buttons[index] = button

    def set_track(self, track):
        self.__track = track
        if track:
            self.__color = toHSB(track.color)[1]
            self._output_meter_changed.subject = track
        else:
            self._output_meter_changed.subject = None
        return

    def to_bar(self, value):
        return (
         value >= 3 and self.__color + 2 or value == 2 and self.__color or 0,
         value >= 5 and self.__color + 2 or value == 4 and self.__color or 0,
         value >= 7 and self.__color + 2 or value == 8 and self.__color or 0,
         value >= 9 and self.__color + 2 or value == 9 and self.__color or 0)

    @subject_slot('output_meter_level')
    def _output_meter_changed(self):
        if self.__track:
            val = int(10 * self.__track.output_meter_level)
            if val != self.__last_meter_val:
                self.__last_bar = self.to_bar(val)
                self.send_color()

    def send_color(self):
        if self.__track:
            self.__buttons[0].send_color_direct(self.__last_bar[0])
            self.__buttons[1].send_color_direct(self.__last_bar[1])
            self.__buttons[2].send_color_direct(self.__last_bar[2])
            self.__buttons[3].send_color_direct(self.__last_bar[3])
        else:
            for button in self.__buttons:
                button.send_color_direct(0)

    def unbind(self):
        self.__track = None
        self._output_meter_changed.subject = None
        return


class LevelIndicatorMode(MaschineMode):
    __track_handlers = None

    def __init__(self, *a, **k):
        super(LevelIndicatorMode, self).__init__(*a, **k)
        self.__track_handlers = [ LevelTracks(idx) for idx in range(4) ]

    def init_elements(self):
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                self.__track_handlers[column].set_button(button, 3 - row)

    def gettrack(self, index, off):
        tracks = self.song().visible_tracks
        if index + off < len(tracks):
            return tracks[index + off]
        return

    def refresh(self):
        if self._active:
            for handler in self.__track_handlers:
                handler.send_color()

    def _assign_tracks(self):
        self._tracks_change.subject = self.song()
        self._visible_changed.subject = self.song()
        trackoff = self.canonical_parent._session.track_offset()
        for i in range(4):
            handler = self.__track_handlers[i]
            handler.unbind()
            track = self.gettrack(i, trackoff)
            handler.set_track(track)

    def _deassign(self):
        self._tracks_change.subject = None
        self._visible_changed.subject = None
        for handler in self.__track_handlers:
            handler.unbind()

        return

    @subject_slot('tracks')
    def _tracks_change(self):
        self._assign_tracks()
        self.refresh()

    @subject_slot('visible_tracks')
    def _visible_changed(self):
        self._assign_tracks()
        self.refresh()

    def enter(self):
        self._active = True
        self._assign_tracks()
        self.refresh()

    def exit(self):
        self._active = False
        self._deassign()
