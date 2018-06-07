# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/OpenLabs/__init__.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
import Live
from .OpenLabs import OpenLabs

def create_instance(c_instance):
    u""" Creates and returns the OpenLabs script """
    return OpenLabs(c_instance)
