# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/NotifyingControlElement.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from .SubjectSlot import Subject, SubjectEvent
from .ControlElement import ControlElement

class NotifyingControlElement(Subject, ControlElement):
    u"""
    Class representing control elements that can send values
    """
    __subject_events__ = (
     SubjectEvent(name='value', doc=' Called when the control element receives a MIDI value\n                             from the hardware '),)
