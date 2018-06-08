# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\MaschineClipSlotComponent.py
# Compiled at: 2017-08-10 18:34:01
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SubjectSlot import subject_slot
from Constants import DEFAULT_CLIP_INIT_SIZE

class MaschineClipSlotComponent(ClipSlotComponent):
    """
    Clip Slot Component for Maschine
    """
    _modifier = None

    def __init__(self, *a, **k):
        super(MaschineClipSlotComponent, self).__init__(*a, **k)
        self.__index = (0, 0)

    def set_modifier(self, modifier):
        self._modifier = modifier

    def set_index(self, index):
        self.__index = index

    def get_index(self):
        return self.__index

    def get_track(self):
        if self._clip_slot is not None:
            return self._clip_slot.canonical_parent
        return

    @subject_slot('value')
    def _launch_button_value(self, value):
        if self.is_enabled():
            if self._modifier and self._modifier.in_spec_mode():
                self._modifier.handle_edit(self, value)
            elif self._clip_slot is not None:
                track = self._clip_slot.canonical_parent
                if track.has_midi_input:
                    self._modifier.do_midi_launch(self, value)
                else:
                    self._do_launch_clip(value)
        return

    def get_launch_button(self):
        return self._launch_button_value_slot.subject
