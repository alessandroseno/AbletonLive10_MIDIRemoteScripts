# uncompyle6 version 3.2.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.10 (default, Feb  7 2017, 00:08:15) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.34)]
# Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2ChannelDeviceComponent.py
# Compiled at: 2014-04-08 15:41:36
from _Framework.DeviceComponent import DeviceComponent
from LC2Sysex import LC2Sysex

class LC2ChannelDeviceComponent(DeviceComponent):

    def __init__(self):
        DeviceComponent.__init__(self)
        self._device_banks = {}

    def bank(self, ud):
        if self._device is not None:
            LC2Sysex.log_message('device')
            if ud:
                num_banks = self.number_of_parameter_banks(self._device)
                LC2Sysex.log_message('up' + str(num_banks))
                if num_banks > self._bank_index + 1:
                    self._bank_name = ''
                    self._bank_index += 1
                    self.update()
            elif self._bank_index > 0:
                self._bank_name = ''
                self._bank_index -= 1
                self.update()
        return

    def number_of_parameter_banks(self, device):
        result = 0
        if device != None:
            param_count = len(list(device.parameters))
            result = param_count / 4
            if not param_count % 4 == 0:
                result += 1
        return result

    def _assign_parameters(self):
        assert self.is_enabled()
        assert self._device != None
        assert self._parameter_controls != None
        parameters = self._device_parameters_to_map()
        num_controls = len(self._parameter_controls)
        index = self._bank_index * num_controls
        for control in self._parameter_controls:
            if index < len(parameters):
                control.connect_to(parameters[index])
            else:
                control.release_parameter()
            index += 1

        return