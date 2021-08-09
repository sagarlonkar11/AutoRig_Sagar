"""
Main module for Human rig setup
"""

from maya import cmds

from rigLib.base import module
from rigLib.base import control

from rigLib.rig import spine
from rigLib.rig import neck
from rigLib.rig import ikChain
from rigLib.rig import leg
from rigLib.rig import hand
from rigLib.rig import head_parts

from rigLib.utils import joint

from . import human_deform
from . import project

scene_scale = project.scene_scale

project_path = project.project_path
model_file_path = '%s/%s/model/%s_model.ma'
builders_scene_file_path = '%s/%s/builder/%s_builder.ma'


def build(character_name):
    """
    Main function to build character Rig
    :type character_name: object
    :param character_name:
    :return:
    """

    # new Scene
    cmds.file(new=True, f=True)

    # import builders scene
    model_builder_file = builders_scene_file_path % (project_path, character_name, character_name)
    cmds.file(model_builder_file, i=1)

    head_joint = cmds.ls('*head*', type='joint')[0]
    # make base class
    base_rig = module.Base(character_name=character_name, scale=scene_scale, main_control_attach_obj=head_joint)

    # import models
    model_file = model_file_path % (project_path, character_name, character_name)
    cmds.file(model_file, i=1)

    # parent model
    model_grp = '%s_model_grp' % character_name
    cmds.parent(model_grp, base_rig.modelGrp)

    root_joint = cmds.ls('*root*', type='joint')
    # parent root to base
    cmds.parent(root_joint, base_rig.jointsGrp)

    # deform setup
    human_deform.build(base_rig, character_name)

    # control setup
    make_control_setup(base_rig)

    # delete builder group
    builder_group = 'builder_group'
    cmds.delete(builder_group)


def make_control_setup(base_rig):
    """
    make control setup
    :param base_rig:
    :return:
    """
    # extracting some joint information
    spine_joints = cmds.ls('spine*', type='joint')
    root_joint = cmds.ls('*root*', type='joint')[0]
    head_joint = cmds.ls('*head*', type='joint')[0]
    neck_joints = cmds.ls('*neck*', type='joint')
    if cmds.objExists('tail'):
        tail_joints = joint.list_hierarchy('tail')
    pelvis_joint = cmds.ls('*pelvis*', type='joint')
    tongue_joints = joint.list_hierarchy('tongue')
    jaw_joint = 'jaw'

    # spine
    spine_curve = 'spine_curve'
    body_locator = 'spine_locator'
    chest_locator = 'chest_locator'
    pelvis_locator = 'hip_locator'
    prefix = 'spine'

    spine_rig = spine.build(spine_joints=spine_joints,
                            root_joints=root_joint,
                            spine_curve=spine_curve,
                            body_locator=body_locator,
                            chest_locator=chest_locator,
                            pelvis_locator=pelvis_locator,
                            prefix=prefix,
                            rig_scale=scene_scale,
                            base_rig=base_rig
                            )

    # neck setup
    neck_curve = 'neck_curve'

    neck_rig = neck.build(neck_joints=neck_joints,
                          head_joint=head_joint,
                          neck_curve=neck_curve,
                          prefix='neck',
                          rig_scale=scene_scale,
                          base_rig=base_rig
                          )

    cmds.parentConstraint(spine_joints[-1], neck_rig['base_attach_grp'], mo=1)
    cmds.parentConstraint(spine_rig['chest_control'].C, neck_rig['body_attach_grp'], mo=1)
    cmds.parentConstraint(spine_joints[-1], neck_rig['body_attach_grp'], mo=1)
    cmds.parentConstraint('global1_ctrl', neck_rig['body_attach_grp'], mo=1)

    # tail
    if cmds.objExists('tail'):
        chain_curve = 'tail_curve'

        tail_rig = ikChain.build(chain_joints=tail_joints,
                                 chain_curve=chain_curve,
                                 prefix='tail',
                                 rig_scale=scene_scale,
                                 smallest_scale_precentage=0.4,
                                 fk_parenting=True,
                                 base_rig=base_rig
                                 )

        cmds.parentConstraint(pelvis_joint, tail_rig['base_attach_grp'], mo=1)

    # tongue
    if cmds.objExists('tongue'):
        chain_curve = 'tongue_curve'

        tongue_rig = ikChain.build(chain_joints=tongue_joints,
                                   chain_curve=chain_curve,
                                   prefix='tongue',
                                   rig_scale=scene_scale * 0.2,
                                   smallest_scale_precentage=0.3,
                                   fk_parenting=True,
                                   base_rig=base_rig
                                   )

        cmds.parentConstraint(jaw_joint, tongue_rig['base_attach_grp'], mo=1)

    # left Arm
    left_arm_joints = ['l_shoulder1',
                       'l_arm',
                       'l_foreArm',
                       'l_hand']
    left_top_finger_joints = ['l_handPinky1',
                              'l_handRing1',
                              'l_handMiddle1',
                              'l_handIndex1',
                              'l_handThumb1']
    left_hand_pv_locator = 'l_elbow_poleVector'

    left_arm_rig = hand.build(hand_joints=left_arm_joints,
                              top_finger_joints=left_top_finger_joints,
                              pv_locator=left_hand_pv_locator,
                              clavicle_joint='l_clavicle',
                              prefix='l_arm',
                              rig_scale=scene_scale,
                              base_rig=base_rig
                              )

    cmds.parentConstraint(spine_joints[-1], left_arm_rig['base_attach_grp'], mo=1)
    cmds.parentConstraint(spine_rig['body_control'].C, left_arm_rig['body_attach_grp'], mo=1)
    cmds.parentConstraint(spine_rig['body_control'].C, left_arm_rig['hand_ctrl'].Off, mo=1)

    # right Arm
    right_arm_joints = ['r_shoulder1',
                        'r_arm',
                        'r_foreArm',
                        'r_hand']
    right_top_finger_joints = ['r_handPinky1',
                               'r_handRing1',
                               'r_handMiddle1',
                               'r_handIndex1',
                               'r_handThumb1']
    right_hand_pv_locator = 'r_elbow_poleVector'

    right_arm_rig = hand.build(hand_joints=right_arm_joints,
                               top_finger_joints=right_top_finger_joints,
                               pv_locator=right_hand_pv_locator,
                               clavicle_joint='r_clavicle',
                               prefix='r_arm',
                               rig_scale=scene_scale,
                               base_rig=base_rig
                               )

    cmds.parentConstraint(spine_joints[-1], right_arm_rig['base_attach_grp'], mo=1)
    cmds.parentConstraint(spine_rig['body_control'].C, right_arm_rig['body_attach_grp'], mo=1)
    cmds.parentConstraint(spine_rig['body_control'].C, right_arm_rig['hand_ctrl'].Off, mo=1)

    # left leg
    left_leg_joints = ['l_hip',
                       'l_leg',
                       'l_foot',
                       'l_toeBase']
    left_top_finger_joints = ['l_legThumb1',
                              'l_legIndex1',
                              'l_legMiddle1',
                              'l_legRing1',
                              'l_legPinky1']
    left_hand_pv_locator = 'l_leg_poleVector'

    left_leg_rig = leg.build(leg_joints=left_leg_joints,
                             top_toe_joints=left_top_finger_joints,
                             pv_locator=left_hand_pv_locator,
                             clavicle_joint='',
                             prefix='l_leg',
                             rig_scale=scene_scale,
                             base_rig=base_rig
                             )

    cmds.parentConstraint(spine_joints[-1], left_leg_rig['base_attach_grp'], mo=1)
    cmds.parentConstraint(spine_rig['body_control'].C, left_leg_rig['body_attach_grp'], mo=1)

    # right leg
    right_leg_joints = ['r_hip',
                        'r_leg',
                        'r_foot',
                        'r_toeBase']
    right_top_finger_joints = ['r_legThumb1',
                               'r_legIndex1',
                               'r_legMiddle1',
                               'r_legRing1',
                               'r_legPinky1']
    right_hand_pv_locator = 'r_leg_poleVector'

    right_leg_rig = leg.build(leg_joints=right_leg_joints,
                              top_toe_joints=right_top_finger_joints,
                              pv_locator=right_hand_pv_locator,
                              clavicle_joint='',
                              prefix='r_leg',
                              rig_scale=scene_scale,
                              base_rig=base_rig
                              )

    cmds.parentConstraint(spine_joints[-1], right_leg_rig['base_attach_grp'], mo=1)
    cmds.parentConstraint(spine_rig['body_control'].C, right_leg_rig['body_attach_grp'], mo=1)

    # head parts
    left_eye = 'l_eye'
    right_eye = 'r_eye'
    muzzle_joint = []

    head_parts_rig = head_parts.build(head_joint=head_joint,
                                      jaw_joint=jaw_joint,
                                      muzzle_joint=muzzle_joint,
                                      left_eye=left_eye,
                                      right_eye=right_eye,
                                      prefix='headParts',
                                      rig_scale=scene_scale,
                                      base_rig=base_rig
                                      )
