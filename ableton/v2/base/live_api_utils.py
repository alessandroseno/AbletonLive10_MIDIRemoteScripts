# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/base/live_api_utils.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals

def liveobj_changed(obj, other):
    u"""
    Check whether obj and other are not equal, properly handling lost weakrefs.
    
    Use this whenever you cache a Live API object in some variable, and want to check
    whether you need to update the cached object.
    """
    return obj != other or type(obj) != type(other)


def liveobj_valid(obj):
    u"""
    Check whether obj represents a valid Live API obj.
    
    This will return False both if obj represents a lost weakref or is None.
    It's important that Live API objects are not checked using "is None", since this
    would treat lost weakrefs as valid.
    """
    return obj != None
