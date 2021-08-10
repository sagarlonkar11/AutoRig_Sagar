"""
Modules for making rig controls
"""

from maya import cmds


class Control(object):
    """
    class for building rig control
    """

    def __init__(self,
                 prefix='new',
                 scale=1.0,
                 translate_to='',
                 rotate_to='',
                 parent='',
                 shape='circle',
                 lock_channels=['s', 'v']
                 ):
        """
        :param prefix: str. adds prefix name to new object
        :param scale: float, scale values for size of control shapes
        :param translate_to: str, reference object for control position
        :param rotate_to: str, reference object for control rotation
        :param parent: str, object to be parent to new control
        :param shape : str, control shape type
        :param lock_channels: list(str), list of channels on control to be locked and non keyable
        :return None
        """
        control_object = None
        circle_normal = [1, 0, 0]

        if shape in ['circle', 'circleX']:
            circle_normal = [1, 0, 0]

        elif shape == 'circleY':
            circle_normal = [0, 1, 0]

        elif shape == 'circleZ':
            circle_normal = [0, 0, 1]

        elif shape == 'sphere':
            control_object = cmds.circle(n=prefix + '_ctrl', ch=False, normal=[1, 0, 0], radius=scale)[0]
            add_shape = cmds.circle(n=prefix + '_ctrl2', ch=False, normal=[0, 0, 1], radius=scale)[0]
            cmds.parent(cmds.listRelatives(add_shape, s=1), control_object, r=1, s=1)
            cmds.delete(add_shape)

        if not control_object:
            control_object = cmds.circle(n=prefix + '_ctrl', ch=False, normal=circle_normal, radius=scale)[0]

        ctrl_offset = cmds.group(n=prefix + '_Offset_grp', em=1)
        ctrl_fk_offset = cmds.group(n=prefix + '_FK_Const_grp', em=1)
        cmds.parent(ctrl_fk_offset, ctrl_offset)
        cmds.parent(control_object, ctrl_fk_offset)

        # colour control

        ctrl_shapes = cmds.listRelatives(control_object, s=1)
        [cmds.setAttr(s + '.ove', 1) for s in ctrl_shapes]

        if prefix.startswith('l_'):
            [cmds.setAttr(s + '.ovc', 6) for s in ctrl_shapes]
        elif prefix.startswith('r_'):
            [cmds.setAttr(s + '.ovc', 13) for s in ctrl_shapes]
        else:
            [cmds.setAttr(s + '.ovc', 22) for s in ctrl_shapes]

        # translate control

        if cmds.objExists(translate_to):
            cmds.delete(cmds.pointConstraint(translate_to, ctrl_offset))

        # rotate control
        if cmds.objExists(rotate_to):
            cmds.delete(cmds.orientConstraint(rotate_to, ctrl_offset))

        # parent control
        if cmds.objExists(parent):
            cmds.parent(ctrl_offset, parent)

        # lock control channels

        single_attribute_lock_list = []
        for lockChannel in lock_channels:
            if lockChannel in ['t', 'r', 's']:
                for axis in ['x', 'y', 'z']:
                    at = lockChannel + axis
                    single_attribute_lock_list.append(at)

            else:
                single_attribute_lock_list.append(lockChannel)
        for at in single_attribute_lock_list:
            cmds.setAttr(control_object + '.' + at, k=0)

        # add public members

        self.C = control_object
        self.Off = ctrl_offset
        self.fk = ctrl_fk_offset


class Locator(object):
    """
    class for building rig Locator
    """

    def __init__(self,
                 prefix='new',
                 scale=1.0,
                 translate_to='',
                 rotate_to='',
                 parent='',
                 shape='circle',
                 lock_channels=['s', 'v']
                 ):
        """
        :param prefix: str. adds prefix name to new object
        :param scale: float, scale values for size of Locator shapes
        :param translate_to: str, reference object for Locator position
        :param rotate_to: str, reference object for Locator rotation
        :param parent: str, object to be parent to new Locator
        :param shape : str, Locator shape type
        :param lock_channels: list(str), list of channels on Locator to be locked and non keyable
        :return None
        """

        locator_object = cmds.spaceLocator(n=prefix + '_loc')[0]

        ctrl_offset = cmds.group(n=prefix + '_Offset_grp', em=1)
        ctrl_fk_offset = cmds.group(n=prefix + '_FK_Const_grp', em=1)
        cmds.parent(ctrl_fk_offset, ctrl_offset)
        cmds.parent(locator_object, ctrl_fk_offset)

        # colour Locator
        locator_shapes = cmds.listRelatives(locator_object, s=1)
        [cmds.setAttr(s + '.ove', 1) for s in locator_shapes]

        if prefix.startswith('l_'):
            [cmds.setAttr(s + '.ovc', 6) for s in locator_shapes]
        elif prefix.startswith('r_'):
            [cmds.setAttr(s + '.ovc', 13) for s in locator_shapes]
        else:
            [cmds.setAttr(s + '.ovc', 22) for s in locator_shapes]
        cmds.setAttr(locator_object + '.displayHandle', 1)
        cmds.setAttr(locator_shapes[0] + '.visibility', 0)

        # translate Locator
        if cmds.objExists(translate_to):
            cmds.delete(cmds.pointConstraint(translate_to, ctrl_offset))

        # rotate Locator
        if cmds.objExists(rotate_to):
            cmds.delete(cmds.orientConstraint(rotate_to, ctrl_offset))

        # parent Locator
        if cmds.objExists(parent):
            cmds.parent(ctrl_offset, parent)

        # lock Locator channels
        single_attribute_lock_list = []
        for lockChannel in lock_channels:
            if lockChannel in ['t', 'r', 's']:
                for axis in ['x', 'y', 'z']:
                    at = lockChannel + axis
                    single_attribute_lock_list.append(at)
            else:
                single_attribute_lock_list.append(lockChannel)
        for at in single_attribute_lock_list:
            cmds.setAttr(locator_object + '.' + at, k=0)

        # add public members
        self.L = locator_object
        self.L_Off = ctrl_offset
        self.L_fk = ctrl_fk_offset
