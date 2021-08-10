"""
Modules for making top rig structure and rig module
"""

from maya import cmds
from rigLib.base import control

sceneObjectType = 'rig'  # type: str


class Base(object):
    """
    class for building top rig structure
    """

    def __init__(self,
                 character_name='new',
                 scale=1.0,
                 main_control_attach_obj=''
                 ):
        """
        :param characterName: str, character name
        :param scale: float, general scale of the rig
        @return: None
        """
        self.topGrp = cmds.group(n=character_name + '_rig_grp', em=1)
        self.rigGrp = cmds.group(n='rig_grp', em=1, p=self.topGrp)
        self.modelGrp = cmds.group(n='model_grp', em=1, p=self.topGrp)

        character_name_attr = 'characterName'
        scene_object_type_attr = 'sceneObjectType'

        for at in [character_name_attr, scene_object_type_attr]:
            cmds.addAttr(self.topGrp, ln=at, dt='string')

        cmds.setAttr(self.topGrp + '.' + character_name_attr, character_name, type='string', lock=1)
        cmds.setAttr(self.topGrp + '.' + scene_object_type_attr, sceneObjectType, type='string', lock=1)

        # add global control

        global1_control = control.Control(prefix='global1',
                                          scale=scale * 20,
                                          parent=self.rigGrp,
                                          lock_channels=['v']
                                          )

        global2_control = control.Control(prefix='global2',
                                          scale=scale * 15,
                                          parent=global1_control.C,
                                          lock_channels=['s', 'v']
                                          )

        self.__flattern_global_control_shapes(global1_control.C)
        self.__flattern_global_control_shapes(global2_control.C)

        for axis in ['y', 'z']:
            cmds.connectAttr(global1_control.C + '.sx', global1_control.C + '.s' + axis)
            cmds.setAttr(global1_control.C + '.s' + axis, k=0)

        # make more grps

        self.jointsGrp = cmds.group(n='joints_grp', em=1, p=global2_control.C)
        self.modulesGrp = cmds.group(n='modules_grp', em=1, p=global2_control.C)
        self.partsGrp = cmds.group(n='parts_grp', em=1, p=self.rigGrp)

        cmds.setAttr(self.rigGrp + '.it', 0, lock=True)

        # make main control
        main_control = control.Control(prefix='main',
                                       scale=scale * 5,
                                       parent=global2_control.C,
                                       translate_to=main_control_attach_obj,
                                       lock_channels=['t', 'r', 's', 'v'],
                                       )
        self._adjust_main_control_shape(main_control, scale)

        if cmds.objExists(main_control_attach_obj):
            cmds.parentConstraint(main_control_attach_obj, main_control.Off, mo=1)

        main_vis_atts = ['modelVis', 'jointsVis']
        main_dis_atts = ['modelDisp', 'jointsDisp']
        main_object_list = [self.modelGrp, self.jointsGrp]
        main_object_vis_div_list = [1, 0]

        # add rig visibility connections
        for at, obj, dfval in zip(main_vis_atts, main_object_list, main_object_vis_div_list):
            cmds.addAttr(main_control.C, ln=at, at='enum', enumName='off:on', k=1, dv=dfval)
            cmds.setAttr(main_control.C + '.' + at, cb=0)
            cmds.connectAttr(main_control.C + '.' + at, obj + '.v')

        # add rig display type connections
        for at, obj in zip(main_dis_atts, main_object_list):
            cmds.addAttr(main_control.C, ln=at, at='enum', enumName='normal:template:reference', k=1, dv=2)
            cmds.setAttr(main_control.C + '.' + at, cb=1)
            cmds.setAttr(obj + '.ove', 1)
            cmds.connectAttr(main_control.C + '.' + at, obj + '.ovdt')

    @staticmethod
    def _adjust_main_control_shape(ctrl, scale):
        # adjust shape of the main control

        ctrl_shapes = cmds.listRelatives(ctrl.C, s=1, type='nurbsCurve')
        cls = cmds.cluster(ctrl_shapes)[1]
        cmds.setAttr(cls + '.ry', 90)
        cmds.delete(ctrl_shapes, ch=1)

        cmds.move(25 * scale, ctrl.Off, moveY=True, relative=True)

    @staticmethod
    def __flattern_global_control_shapes(ctrl_object):
        # flattern controls object shapes

        ctrl_shapes = cmds.listRelatives(ctrl_object, s=1, type='nurbsCurve')
        cls = cmds.cluster(ctrl_shapes)[1]
        cmds.setAttr(cls + '.rz', 90)
        cmds.delete(ctrl_shapes, ch=1)


class Module(object):
    """
    class for building Module rig structure
    """

    def __init__(self,
                 prefix='new',
                 base_object=None
                 ):
        """
        :param prefix: str, prefix to name new oujects
        :param base_object: instance of base.module.Base class
        :return None
        """
        self.topGrp = cmds.group(n=prefix + '_module_grp', em=1)
        self.controlsGrp = cmds.group(n=prefix + 'Controls_grp', em=1, p=self.topGrp)
        self.jointsGrp = cmds.group(n=prefix + 'Joints_grp', em=1, p=self.topGrp)
        self.partsGrp = cmds.group(n=prefix + 'Parts_grp', em=1, p=self.topGrp)
        self.partsNoTransGrp = cmds.group(n=prefix + 'PartsNoTrans_grp', em=1, p=self.topGrp)

        cmds.hide(self.partsGrp, self.partsNoTransGrp)
        cmds.setAttr(self.partsNoTransGrp + '.it', 0)

        # parent module

        if base_object:
            cmds.parent(self.topGrp, base_object.modulesGrp)
