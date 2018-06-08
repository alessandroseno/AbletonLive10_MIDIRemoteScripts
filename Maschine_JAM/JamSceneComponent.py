# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\JamSceneComponent.py
# Compiled at: 2018-03-21 20:20:59
from _Framework.SceneComponent import SceneComponent
from _Framework.Util import nop
from JamClipSlotComponent import JamClipSlotComponent

class JamSceneComponent(SceneComponent):
    """
    Special Scene Component for Maschine
    """
    clip_slot_component_type = JamClipSlotComponent

    def __init__(self, num_slots=0, tracks_to_use_callback=nop, *a, **k):
        super(JamSceneComponent, self).__init__(num_slots, tracks_to_use_callback, *a, **k)
