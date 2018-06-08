# Embedded file name: C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\Maschine_JAM\Max4LiveComponent.py
# Compiled at: 2018-03-20 20:54:44
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class Max4LiveComponent(ControlSurfaceComponent):

    def __init__(self, controls, mode_handler, matrix_state, *a, **k):
        super(Max4LiveComponent, self).__init__(self, *a, **k)
        self._controls = dict(map(lambda x: (x.name, x), controls))
        self._grabbed_controls = []
        self._mode_handler = mode_handler
        self.__matrix_state = matrix_state

    def disconnect(self):
        for control in self._grabbed_controls[:]:
            self.release_control(control)

        super(Max4LiveComponent, self).disconnect()

    def set_control_element(self, control, grabbed):
        if hasattr(control, 'release_parameter'):
            control.release_parameter()
        control.reset()

    def batch_matrix(self, which, *a, **k):
        if which == 'group':
            control_track = self._controls['Track_Select_Button_Matrix']
            if control_track and control_track.grabbed:
                self.__matrix_state.update_values(control_track, a)
        else:
            if which == 'scene':
                control_scene = self._controls['Scene_Launch_Button_Matrix']
                if control_scene and control_scene.grabbed:
                    self.__matrix_state.update_values(control_scene, a)
            else:
                if which == 'matrix':
                    control_matrix = self._controls['Button_Matrix']
                    if control_matrix and control_matrix.grabbed:
                        self.__matrix_state.update_values(control_matrix, a)
                else:
                    if which == 'all':
                        self.__matrix_state.update_all_values(a)

    def get_control_names(self):
        return self._controls.keys()

    def get_control(self, control_name):
        if control_name in self._controls:
            return self._controls[control_name]
        if control_name == 'Jam_Session':
            return self.canonical_parent._session
        return

    def grab_control(self, control):
        if control not in self._controls.values():
            raise AssertionError
        else:
            if hasattr(control, 'switch_to_user_action'):
                control.switch_to_user_action()
                self.canonical_parent._main_mode_container.enter_user_mode()
            else:
                if control not in self._grabbed_controls and hasattr(control, 'grab_control'):
                    control.grab_control()
                    self._grabbed_controls.append(control)

    def release_control(self, control):
        if control not in self._controls.values():
            control.resource.release(self)
        else:
            if hasattr(control, 'exit_user_action'):
                control.exit_user_action()
                self.canonical_parent._main_mode_container.exit_user_mode()
            else:
                if control in self._grabbed_controls and hasattr(control, 'release_control'):
                    control.release_control()
                    self._grabbed_controls.remove(control)

    def update(self):
        pass
