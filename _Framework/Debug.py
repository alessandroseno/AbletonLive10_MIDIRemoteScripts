# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/Debug.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
enable_debug_output = True

def debug_print(*a):
    u""" Special function for debug output """
    if enable_debug_output:
        print((' ').join(map(str, a)))
