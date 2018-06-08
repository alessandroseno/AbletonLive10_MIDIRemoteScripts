# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\MaschineSceneComponent.py
# Compiled at: 2017-08-10 18:34:01
from _Framework.SceneComponent import SceneComponent
from _Framework.Util import nop
from MaschineClipSlotComponent import MaschineClipSlotComponent

class MaschineSceneComponent(SceneComponent):
    """
    Special Scene Component for Maschine
    """
    clip_slot_component_type = MaschineClipSlotComponent

    def __init__(self, num_slots=0, tracks_to_use_callback=nop, *a, **k):
        super(MaschineSceneComponent, self).__init__(num_slots, tracks_to_use_callback, *a, **k)
