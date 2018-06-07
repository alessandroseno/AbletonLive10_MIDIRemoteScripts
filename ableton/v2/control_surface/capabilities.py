# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/capabilities.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
GENERIC_SCRIPT_KEY = 'generic_script'
PORTS_KEY = 'ports'
CONTROLLER_ID_KEY = 'controller_id'
TYPE_KEY = 'surface_type'
FIRMWARE_KEY = 'firmware_version'
AUTO_LOAD_KEY = 'auto_load'
VENDORID = 'vendor_id'
PRODUCTIDS = 'product_ids'
MODEL_NAMES = 'model_names'
DIRECTIONKEY = 'direction'
PORTNAMEKEY = 'name'
MACNAMEKEY = 'mac_name'
PROPSKEY = 'props'
HIDDEN = 'hidden'
SYNC = 'sync'
SCRIPT = 'script'
NOTES_CC = 'notes_cc'
REMOTE = 'remote'
PLAIN_OLD_MIDI = 'plain_old_midi'

def __create_port_dict(direction, port_name, mac_name, props):
    assert isinstance(direction, basestring)
    assert isinstance(port_name, basestring)
    assert props == None or type(props) is list
    if props:
        for prop in props:
            if not isinstance(prop, basestring):
                raise AssertionError

    assert mac_name == None or isinstance(mac_name, basestring)
    capabilities = {DIRECTIONKEY: direction, PORTNAMEKEY: port_name, PROPSKEY: props}
    if mac_name:
        capabilities[MACNAMEKEY] = mac_name
    return capabilities


def inport(port_name='', props=[], mac_name=None):
    u""" Generate a ..."""
    return __create_port_dict('in', port_name, mac_name, props)


def outport(port_name='', props=[], mac_name=None):
    u""" Generate a ..."""
    return __create_port_dict('out', port_name, mac_name, props)


def controller_id(vendor_id, product_ids, model_name):
    u""" Generate a hardwareId dict"""
    assert type(vendor_id) is int
    assert type(product_ids) is list
    for product_id in product_ids:
        if not type(product_id) is int:
            raise AssertionError

    assert isinstance(model_name, (basestring, list))
    model_names = model_name if type(model_name) is list else [model_name]
    return {VENDORID: vendor_id, PRODUCTIDS: product_ids, MODEL_NAMES: model_names}
