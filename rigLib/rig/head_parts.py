"""
headParts @ rig
"""

import maya.cmds as cmds

from rigLib.base import module
from rigLib.base import control


def build(head_joint,
          jaw_joint,
          muzzle_joint,
          left_eye,
          right_eye,
          prefix='headParts',
          rig_scale=1.0,
          base_rig=None
          ):
    """
    :param head_joint: str, name of head joint
    :param jaw_joint: str, name of jaw joint
    :param muzzle_joint: list(str), list with 2 muzzle joints chain
    :param left_eye: str, name of left eye joint
    :param right_eye: str, name of right eye joint
    :param rig_scale: float, scale factor for size of controls
    :param base_rig: baseRig: instance of base.module.Base class
    :return: dictionary with rig module objects
    :param prefix: str, prefix name used for the head parts

    """

    # make rig module

    rig_module = module.Module(prefix=prefix, base_object=base_rig)

    # make attach groups

    head_attach_grp = cmds.group(n=prefix + '_head_attach_grp', em=1, p=rig_module.controlsGrp)
    cmds.parentConstraint(head_joint, head_attach_grp, mo=1)

    # make controls

    jaw_ctrl = control.Control(prefix='jaw',
                               translate_to=jaw_joint,
                               rotate_to=jaw_joint,
                               scale=rig_scale * 7,
                               parent=head_attach_grp,
                               shape='circleX'
                               )
    if muzzle_joint:
        muzzle_ctrl1 = control.Control(prefix='muzzle1',
                                       translate_to=muzzle_joint[0],
                                       rotate_to=muzzle_joint[0],
                                       scale=rig_scale,
                                       parent=head_attach_grp,
                                       lock_channels=['t', 's', 'v']
                                       )

        muzzle_ctrl2 = control.Control(prefix='muzzle2',
                                       translate_to=muzzle_joint[1],
                                       rotate_to=muzzle_joint[1],
                                       scale=rig_scale,
                                       parent=muzzle_ctrl1.C,
                                       lock_channels=['t', 's', 'v']
                                       )
        # attach muzzle joints
        cmds.orientConstraint(muzzle_ctrl1.C, muzzle_joint[0])
        cmds.orientConstraint(muzzle_ctrl2.C, muzzle_joint[1])

    left_eye_ctrl = control.Control(prefix='l_eye',
                                    translate_to=left_eye,
                                    rotate_to=left_eye,
                                    scale=rig_scale * 3,
                                    parent=head_attach_grp,
                                    shape='circleX',
                                    lock_channels=['t', 's', 'v']
                                    )

    right_eye_ctrl = control.Control(prefix='r_eye',
                                     translate_to=right_eye,
                                     rotate_to=right_eye,
                                     scale=rig_scale * 3,
                                     parent=head_attach_grp,
                                     shape='circleX',
                                     lock_channels=['t', 's', 'v']
                                     )

    # attach joints
    cmds.parentConstraint(jaw_ctrl.C, jaw_joint)
    cmds.orientConstraint(left_eye_ctrl.C, left_eye)
    cmds.orientConstraint(right_eye_ctrl.C, right_eye)

    return {'module': rig_module}








