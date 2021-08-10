"""
leg @ rig
"""
from maya import cmds

from rigLib.base import module
from rigLib.base import control

from rigLib.utils import joint


def build(leg_joints,
          top_toe_joints,
          pv_locator,
          clavicle_joint='',
          prefix='l_leg',
          rig_scale=1.0,
          base_rig=None
          ):
    """
    :param leg_joints: list(str), shoulder, elbow toe, end toe
    :param top_toe_joints: list(str), top metacarpal toe joint
    :param pv_locator: str, reference locator of position of pole vector control
    :param clavicle_joint: str, optional clavicle joint, parent of shoulder or top leg joint
    :param prefix: str, prefix to name new objects
    :param rig_scale: float, scale factor of size of controls
    :param base_rig: instance of base module base class
    :return: dictionary with rig module objects
    """

    # make rig module
    rig_module = module.Module(prefix=prefix, base_object=base_rig)

    # make attach grps
    body_attach_grp = cmds.group(n=prefix + '_bodyAttach_grp', em=1, p=rig_module.partsGrp)
    base_attach_grp = cmds.group(n=prefix + '_baseAttach_grp', em=1, p=rig_module.partsGrp)

    # make FK controls
    if clavicle_joint:
        fk_clavicle_ctrl = control.Locator(prefix=prefix + '_FK_clavicle',
                                           translate_to=clavicle_joint,
                                           rotate_to=clavicle_joint,
                                           scale=rig_scale * 10,
                                           parent=rig_module.controlsGrp,
                                           shape='sphere',
                                           lock_channels=['ty', 'rx', 'rz', 's', 'v']
                                           )

    fk_hip_ctrl = control.Locator(prefix=prefix + '_FK_hip',
                                  translate_to=leg_joints[0],
                                  rotate_to=leg_joints[0],
                                  scale=rig_scale * 10,
                                  parent=rig_module.controlsGrp,
                                  lock_channels=['t', 's'],
                                  shape='circleY'
                                  )

    fk_knee_ctrl = control.Locator(prefix=prefix + '_FK_knee',
                                   translate_to=leg_joints[1],
                                   rotate_to=leg_joints[1],
                                   scale=rig_scale,
                                   parent=fk_hip_ctrl.L,
                                   lock_channels=['t', 's'],
                                   shape='sphere'
                                   )

    fk_ankle_ctrl = control.Control(prefix=prefix + '_FK_ankle',
                                    translate_to=leg_joints[2],
                                    rotate_to=leg_joints[2],
                                    scale=rig_scale * 6,
                                    parent=fk_knee_ctrl.L,
                                    lock_channels=['t', 's'],
                                    shape='sphere'
                                    )
    fk_ball_ctrl = control.Locator(prefix=prefix + '_FK_ball',
                                   translate_to=leg_joints[3],
                                   rotate_to=leg_joints[3],
                                   scale=rig_scale * 6,
                                   parent=fk_ankle_ctrl.C,
                                   lock_channels=['t', 's'],
                                   shape='sphere'
                                   )
    # make IK controls
    if clavicle_joint:
        clavicle_ctrl = control.Control(prefix=prefix + '_clavicle',
                                        translate_to=clavicle_joint,
                                        rotate_to=clavicle_joint,
                                        scale=rig_scale * 3,
                                        parent=rig_module.controlsGrp,
                                        shape='sphere',
                                        lock_channels=['ty', 'rx', 'rz', 's', 'v']
                                        )

    ankle_ctrl = control.Control(prefix=prefix + '_ankle',
                                 translate_to=leg_joints[2],
                                 scale=rig_scale * 7,
                                 parent=rig_module.controlsGrp,
                                 shape='circleY'
                                 )
    leg_local_transform = cmds.createNode('transform', name=prefix + '_leg_local_transform')
    cmds.parent(leg_local_transform, ankle_ctrl.Off)
    cmds.parentConstraint(leg_joints[2], leg_local_transform)

    ball_ctrl = control.Control(prefix=prefix + '_ball',
                                translate_to=leg_joints[3],
                                rotate_to=leg_joints[3],
                                scale=rig_scale * 5,
                                parent=ankle_ctrl.C,
                                shape='circleX'
                                )
    pole_vector_ctrl = control.Control(prefix=prefix + '_PV',
                                       translate_to=pv_locator,
                                       scale=rig_scale,
                                       parent=rig_module.controlsGrp,
                                       shape='sphere'
                                       )
    # make IK handles
    if clavicle_joint:
        clavicle_ik = cmds.ikHandle(n=prefix + '_clavicle_ikh', sol='ikSCsolver',
                                    sj=clavicle_joint,
                                    ee=leg_joints[0]
                                    )[0]
    leg_ik = cmds.ikHandle(n=prefix + '_main_ikh',
                           sol='ikRPsolver',
                           sj=leg_joints[0],
                           ee=leg_joints[2]
                           )[0]
    ball_ik = cmds.ikHandle(n=prefix + '_Ball_ikh',
                            sol='ikSCsolver',
                            sj=leg_joints[2],
                            ee=leg_joints[3]
                            )[0]

    cmds.hide(leg_ik, ball_ik)

    # attach controls
    # removing this for some time till I figure out space switch
    # cmds.parentConstraint(body_attach_grp, pole_vector_ctrl.Off, mo=1)

    if clavicle_joint:
        cmds.parentConstraint(base_attach_grp, clavicle_ctrl.Off, mo=1)

    # attach objects to controls
    cmds.parent(leg_ik, ball_ctrl.C)
    cmds.parent(ball_ik, ankle_ctrl.C)  # main_toe_ik

    cmds.poleVectorConstraint(pole_vector_ctrl.C, leg_ik)

    if clavicle_joint:
        cmds.parent(clavicle_ik, clavicle_ctrl.C)
        cmds.pointConstrint(clavicle_ctrl.C, clavicle_joint)

    # make pole vector connection line
    pv_line_pose1 = cmds.xform(leg_joints[1], q=1, t=1, ws=1)
    pv_line_pose2 = cmds.xform(pv_locator, q=1, t=1, ws=1)
    pole_vector_curve = cmds.curve(n=prefix + '_PV_curve', d=1, p=[pv_line_pose1, pv_line_pose2])
    cmds.cluster(pole_vector_curve + '.cv[0]',
                 n=prefix + '_pv1_cluster',
                 wn=[leg_joints[1], leg_joints[1]],
                 bs=True)
    cmds.cluster(pole_vector_curve + '.cv[1]',
                 n=prefix + '_pv1_cluster',
                 wn=[pole_vector_ctrl.C, pole_vector_ctrl.C],
                 bs=True)
    cmds.parent(pole_vector_curve, rig_module.controlsGrp)
    cmds.setAttr(pole_vector_curve + '.template', 1)
    cmds.setAttr(pole_vector_curve + '.it', 0)

    # creating toe FK controls
    toe_fk_constraints = []
    toe_fk_constraint_weights = []
    fk_toe_locators = []
    for top_toe_joint in top_toe_joints:
        listed_joints = joint.list_hierarchy(top_toe_joint, with_end_joints=False)
        toe_fk_loc = []
        for each in listed_joints:
            fk_toe_locator = control.Locator(prefix=each + '_FK_toes',
                                             translate_to=each,
                                             rotate_to=each,
                                             scale=2,
                                             parent=leg_local_transform
                                             )
            toe_fk_loc.append(fk_toe_locator)
            fk_toe_locators.append(fk_toe_locator)
        for i, j in enumerate(listed_joints):
            print toe_fk_loc[i].L, j
            cmds.orientConstraint(toe_fk_loc[i].L, j, mo=1)
            fk_toe_ctrl_constraint = cmds.orientConstraint(toe_fk_loc[i].L, j, mo=1)
            fk_toe_ctrl_constraint_weight = cmds.orientConstraint(fk_toe_ctrl_constraint, q=True, wal=True)
            toe_fk_constraints.append(fk_toe_ctrl_constraint)
            toe_fk_constraint_weights.append(fk_toe_ctrl_constraint_weight)

        toe_length = len(toe_fk_loc)
        toe_fk_loc.reverse()
        if toe_fk_loc:
            for each in range(toe_length):
                if each <= toe_length - 2:
                    print each
                    cmds.parent(toe_fk_loc[each].L_Off, toe_fk_loc[each + 1].L)

    # creating IK toe controls
    toe_ik_control = []
    for top_toe_joint in top_toe_joints:
        toe_prefix = prefix + top_toe_joint
        toe_end_joint = cmds.listRelatives(top_toe_joint, ad=1, type='joint')[0]

        toe_ik_ctrl = control.Control(prefix=toe_prefix,
                                      translate_to=toe_end_joint,
                                      scale=rig_scale,
                                      parent=leg_local_transform,
                                      shape='circleY'
                                      )

        toe_ik_control.append(toe_ik_ctrl)

    for i, top_toe_joint in enumerate(top_toe_joints):
        toe_prefix = prefix + top_toe_joint
        toe_joints = joint.list_hierarchy(top_toe_joint)

        toe_ik = cmds.ikHandle(n=toe_prefix + '_ikh',
                               sol='ikSCsolver',
                               sj=toe_joints[0],
                               ee=toe_joints[-1]
                               )[0]

        cmds.hide(toe_ik)
        cmds.parent(toe_ik, toe_ik_control[i].C)

    # creating some fk constraint
    fk_hip_ctrl_constraint = cmds.orientConstraint(fk_hip_ctrl.L, leg_joints[0], mo=1)
    fk_hip_ctrl_constraint_weight = cmds.orientConstraint(fk_hip_ctrl_constraint, q=True, wal=True)

    fk_knee_ctrl_constraint = cmds.orientConstraint(fk_knee_ctrl.L, leg_joints[1], mo=1)
    fk_knee_ctrl_constraint_weight = cmds.orientConstraint(fk_knee_ctrl_constraint, q=True, wal=True)
    
    fk_ankle_ctrl_constraint = cmds.orientConstraint(fk_ankle_ctrl.C, leg_joints[2], mo=1)
    fk_ankle_ctrl_constraint_weight = cmds.orientConstraint(fk_ankle_ctrl_constraint, q=True, wal=True)

    ankle_ctrl_constraint = cmds.orientConstraint(ankle_ctrl.C, leg_joints[2], mo=1)
    ankle_ctrl_constraint_weight = cmds.orientConstraint(ankle_ctrl_constraint, q=True, wal=True)

    fk_ball_ctrl_constraint = cmds.orientConstraint(fk_ball_ctrl.L, leg_joints[3], mo=1)
    fk_ball_ctrl_constraint_weight = cmds.orientConstraint(fk_ball_ctrl_constraint, q=True, wal=True)

    ball_ctrl_constraint = cmds.orientConstraint(ball_ctrl.C, leg_joints[3], mo=1)
    ball_ctrl_constraint_weight = cmds.orientConstraint(ball_ctrl_constraint, q=True, wal=True)
    
    if clavicle_joint:
        fk_clavicle_ctrl_constraint = cmds.orientConstraint(fk_clavicle_ctrl.L, clavicle_joint, mo=1)
        fk_clavicle_ctrl_constraint_weight = cmds.orientConstraint(fk_clavicle_ctrl_constraint, q=True, wal=True)

        clavicle_ctrl_constraint = cmds.orientConstraint(clavicle_ctrl.C, clavicle_joint, mo=1)
        clavicle_ctrl_constraint_weight = cmds.orientConstraint(clavicle_ctrl_constraint, q=True, wal=True)

    # IK FK switch
    # creating IK FK switch locator shape
    ik_fk_switch = control.Locator(prefix=prefix + '_ik_fk_switch',
                                   translate_to=rig_module.partsNoTransGrp,
                                   rotate_to=rig_module.partsNoTransGrp,
                                   parent=rig_module.partsNoTransGrp
                                   )
    ik_fk_switch_shape = cmds.listRelatives(ik_fk_switch.L, s=True)

    cmds.addAttr(ik_fk_switch_shape, longName='Leg_ik_fk_switch', defaultValue=1.0, minValue=0, maxValue=1, k=1)
    cmds.addAttr(ik_fk_switch_shape, longName='Toe_ik_fk_switch', defaultValue=1.0, minValue=0, maxValue=1, k=1)
    cmds.parent(ik_fk_switch_shape, ankle_ctrl.C, add=True, shape=True)
    cmds.parent(ik_fk_switch_shape, fk_ankle_ctrl.C, add=True, shape=True)

    # connecting FINGER, HAND and CLAVICLE IKH to IK_FK_switch
    for ikh in toe_ik:
        cmds.connectAttr(ik_fk_switch_shape[0] + '.Toe_ik_fk_switch',
                         ikh + '.ikBlend')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     leg_ik + '.ikBlend')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     clavicle_ik + '.ikBlend')
    for i, constraint in enumerate(toe_fk_constraint_weights):
        cmds.connectAttr(ik_fk_switch_shape[0] + '.Toe_ik_fk_switch',
                         str(toe_fk_constraints[i][0]) + '.' + str(constraint[0]))

    # connecting CLAVICLE Constraint to IK_FK switch
    fk_clavicle_reverse_constraint = cmds.createNode('reverse', name='fk_clavicle_reverse_constraint')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     fk_clavicle_reverse_constraint + '.input.inputX')
    cmds.connectAttr(fk_clavicle_reverse_constraint + '.output.outputX',
                     fk_clavicle_ctrl_constraint[0] + '.' + fk_clavicle_ctrl_constraint_weight[0])

    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     clavicle_ctrl_constraint[0] + '.' + clavicle_ctrl_constraint_weight[1])

    # connecting SHOULDER Constraint to IK_FK switch
    shoulder_reverse_node = cmds.createNode('reverse', name='shoulder_reverse')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     shoulder_reverse_node + '.input.inputX')

    # connecting ELBOW Constraint to IK_FK switch
    elbow_reverse_node = cmds.createNode('reverse', name='elbow_reverse')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     elbow_reverse_node + '.input.inputX')
    cmds.connectAttr(elbow_reverse_node + '.output.outputX',
                     fk_elbow_ctrl_constraint[0] + '.' + fk_elbow_ctrl_constraint_weight[0])

    # connecting HAND Constraint to IK_FK switch
    fk_hand_reverse_constraint = cmds.createNode('reverse', name='fk_hand_reverse_constraint')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     fk_hand_reverse_constraint + '.input.inputX')
    cmds.connectAttr(fk_hand_reverse_constraint + '.output.outputX',
                     fk_ankle_ctrl_constraint[0] + '.' + fk_ankle_ctrl_constraint_weight[0])

    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     ankle_ctrl_constraint[0] + '.' + ankle_ctrl_constraint_weight[1])

    # connecting control VISIBILITY
    # connecting FK visibility
    hand_visibility_reverse_node = cmds.createNode('reverse', name='hand_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     hand_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(hand_visibility_reverse_node + '.output.outputX',
                     fk_hand_ctrl.C + '.v')

    elbow_visibility_reverse_node = cmds.createNode('reverse', name='elbow_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     elbow_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(elbow_visibility_reverse_node + '.output.outputX',
                     fk_elbow_ctrl.L + '.v')

    shoulder_visibility_reverse_node = cmds.createNode('reverse', name='shoulder_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     shoulder_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(shoulder_visibility_reverse_node + '.output.outputX',
                     fk_shoulder_ctrl.L + '.v')

    clavicle_visibility_reverse_node = cmds.createNode('reverse', name='clavicle_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     clavicle_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(clavicle_visibility_reverse_node + '.output.outputX',
                     fk_clavicle_ctrl.L + '.v')

    # connecting IK visibility
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     hand_ctrl.C + '.v')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Leg_ik_fk_switch',
                     clavicle_ctrl.C + '.v')

    # connecting finger visibility
    for finger_ik in finger_ik_control:
        cmds.connectAttr(ik_fk_switch_shape[0] + '.Toe_ik_fk_switch',
                         finger_ik.C + '.v')
    fk_finger_reverse_node = cmds.createNode('reverse', name='finger_fk_reverse')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Toe_ik_fk_switch',
                     fk_finger_reverse_node + '.input.inputX')
    for fk_loc in fk_finger_locators:
        cmds.connectAttr(fk_finger_reverse_node + '.output.outputX',
                         fk_loc.L + '.v')

    return {'module': rig_module,
            'base_attach_grp': base_attach_grp,
            'body_attach_grp': body_attach_grp
            }
