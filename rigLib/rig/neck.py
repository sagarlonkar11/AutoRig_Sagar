"""
neck @ rig
"""

from maya import cmds
from rigLib.base import module
from rigLib.base import control


def build(neck_joints,
          head_joint,
          neck_curve,
          prefix='neck',
          rig_scale=1,
          base_rig=None):
    """
    :param neck_joints: list(str), list of neck joints
    :param head_joint: str, head joint at the end of neck joint chain
    :param neck_curve: str, name of the neck curve with 5 cv's
    :param prefix: str, prefix to name of the objects
    :param rig_scale: float, scale factor for size of controls
    :param base_rig: instance of base module base class
    :return: dictionary with rig module objects
    """

    # make rig module

    rig_module = module.Module(prefix=prefix, base_object=base_rig)

    # make neck curve clusters

    neck_curve_cvs = cmds.ls(neck_curve + '.cv[*]', fl=1)
    number_of_neck_cv = len(neck_curve_cvs)
    neck_curve_clusters = []
    for i in range(number_of_neck_cv):
        cls = cmds.cluster(neck_curve_cvs[i], n=prefix + 'cluster%d' % (i + 1))[1]
        neck_curve_clusters.append(cls)

    cmds.hide(neck_curve_clusters)

    # parent neck curve
    cmds.parent(neck_curve, rig_module.partsNoTransGrp)

    # make attach grps
    body_attach_grp = cmds.group(n=prefix + '_bodyAttach_grp', em=1, p=rig_module.partsGrp)
    base_attach_grp = cmds.group(n=prefix + '_baseAttach_grp', em=1, p=rig_module.partsGrp)

    cmds.delete(cmds.parentConstraint(neck_joints[0], base_attach_grp))

    # make controls
    head_main_control = control.Control(prefix=prefix + '_HeadMain',
                                        translate_to=neck_joints[-1],
                                        scale=rig_scale * 10,
                                        parent=rig_module.controlsGrp,
                                        shape='circleY'
                                        )
    head_local_control = control.Control(prefix='Head_Local',
                                         translate_to=head_joint,
                                         rotate_to=head_joint,
                                         scale=rig_scale * 15,
                                         parent=head_main_control.C,
                                         shape='sphere'
                                         )

    middle_neck_joint = int(len(neck_joints) / 2)
    middle_control = control.Control(prefix=prefix + '_Middle',
                                     translate_to=neck_curve_clusters[2],
                                     rotate_to=neck_joints[middle_neck_joint],
                                     scale=rig_scale * 7,
                                     parent=rig_module.controlsGrp,
                                     shape='circleY')

    # attach controls
    cmds.parentConstraint(head_main_control.C, base_attach_grp, middle_control.Off, sr=['x', 'y', 'z'], mo=1)
    cmds.orientConstraint(base_attach_grp, middle_control.Off, mo=1)
    cmds.parentConstraint(body_attach_grp, head_main_control.Off, mo=1)

    middle_neck_cv = int(len(neck_curve_clusters) / 2)
    cmds.parent(neck_curve_clusters[middle_neck_cv + 1:], head_main_control.C)
    cmds.parent(neck_curve_clusters[middle_neck_cv], middle_control.C)
    cmds.parent(neck_curve_clusters[:middle_neck_cv], base_attach_grp)

    # attach joints
    cmds.parentConstraint(head_local_control.C, head_joint, mo=1)

    # make IK handle
    neck_ik = cmds.ikHandle(n=prefix + '_ikh',
                            sol='ikSplineSolver',
                            sj=neck_joints[0],
                            ee=neck_joints[-1],
                            c=neck_curve,
                            ccv=0,
                            parentCurve=0)[0]

    cmds.hide(neck_ik)
    cmds.parent(neck_ik, rig_module.partsNoTransGrp)

    # setup IK twist
    cmds.setAttr(neck_ik + '.dTwistControlEnable', 1)
    cmds.setAttr(neck_ik + '.dWorldUpType', 7)
    cmds.setAttr(neck_ik + '.dForwardAxis', 2)
    cmds.setAttr(neck_ik + '.dWorldUpAxis', 6)
    cmds.connectAttr(head_main_control.C + '.worldMatrix[0]', neck_ik + '.dWorldUpMatrixEnd')
    cmds.connectAttr(base_attach_grp + '.worldMatrix[0]', neck_ik + '.dWorldUpMatrix')

    return {'module': rig_module,
            'base_attach_grp': base_attach_grp,
            'body_attach_grp': body_attach_grp,
            'head_main_control_offset_grp': head_main_control.Off
            }
