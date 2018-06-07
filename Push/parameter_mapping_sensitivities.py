# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push/parameter_mapping_sensitivities.py
# Compiled at: 2018-05-12 02:03:19
from __future__ import absolute_import, print_function, unicode_literals
from pushbase.parameter_provider import is_parameter_quantized
CONTINUOUS_MAPPING_SENSITIVITY = 2.0
FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY = 0.01
QUANTIZED_MAPPING_SENSITIVITY = 1.0 / 15.0

def parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    if is_quantized:
        return QUANTIZED_MAPPING_SENSITIVITY
    return CONTINUOUS_MAPPING_SENSITIVITY


def fine_grain_parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    if is_quantized:
        return QUANTIZED_MAPPING_SENSITIVITY
    return FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY
