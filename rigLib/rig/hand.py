"""
hand @ rig
"""
from maya import cmds

from rigLib.base import module
from rigLib.base import control

from rigLib.utils import joint


def build(hand_joints,
          top_finger_joints,
          pv_locator,
          clavicle_joint='',
          prefix='l_hand',
          rig_scale=1.0,
          base_rig=None
          ):
    """
    :param hand_joints: list(str), shoulder, elbow finger, end finger
    :param top_finger_joints: list(str), top metacarpal finger joint
    :param pv_locator: str, reference locator of position of pole vector control
    :param clavicle_joint: str, optional clavicle joint, parent of shoulder or top hand joint
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

    fk_shoulder_ctrl = control.Locator(prefix=prefix + '_FK_Shoulder',
                                       translate_to=hand_joints[1],
                                       rotate_to=hand_joints[1],
                                       scale=rig_scale * 10,
                                       parent=fk_clavicle_ctrl.L,
                                       lock_channels=['t', 's'],
                                       shape='circleY'
                                       )

    fk_elbow_ctrl = control.Locator(prefix=prefix + '_FK_Elbow',
                                    translate_to=hand_joints[2],
                                    rotate_to=hand_joints[2],
                                    scale=rig_scale,
                                    parent=fk_shoulder_ctrl.L,
                                    lock_channels=['t', 's'],
                                    shape='sphere'
                                    )

    fk_hand_ctrl = control.Control(prefix=prefix + '_FK_Hand',
                                   translate_to=hand_joints[3],
                                   rotate_to=hand_joints[3],
                                   scale=rig_scale * 6,
                                   parent=fk_elbow_ctrl.L,
                                   lock_channels=['t', 's'],
                                   shape='sphere'
                                   )

    # make IK controls
    if clavicle_joint:
        clavicle_ctrl = control.Control(prefix=prefix + '_sacpula',
                                        translate_to=clavicle_joint,
                                        rotate_to=clavicle_joint,
                                        scale=rig_scale * 10,
                                        parent=rig_module.controlsGrp,
                                        shape='sphere',
                                        lock_channels=['ty', 's', 'v']
                                        )

    '''
    shoulder_ctrl = control.Control(prefix=prefix + '_shoulder',
                                    translate_to=hand_joints[1],
                                    rotate_to=hand_joints[1],
                                    scale=rig_scale * 10,
                                    parent=rig_module.controlsGrp,
                                    shape='circleY'
                                    )
    '''

    hand_ctrl = control.Control(prefix=prefix + '_hand',
                                translate_to=hand_joints[3],
                                rotate_to=hand_joints[3],
                                scale=rig_scale * 6,
                                parent=rig_module.controlsGrp,
                                shape='sphere'
                                )
    hand_local_transform = cmds.createNode('transform', name=prefix + '_hand_local_transform')
    cmds.parent(hand_local_transform, hand_ctrl.Off)
    cmds.parentConstraint(hand_joints[3], hand_local_transform)

    pole_vector_ctrl = control.Control(prefix=prefix + '_PV',
                                       translate_to=pv_locator,
                                       scale=rig_scale,
                                       parent=rig_module.controlsGrp,
                                       shape='sphere'
                                       )

    # make IK handles
    if clavicle_joint:
        clavicle_ik = cmds.ikHandle(n=prefix + '_clavicle_ikh',
                                    sol='ikSCsolver',
                                    sj=clavicle_joint,
                                    ee=hand_joints[0]
                                    )[0]

    hand_ik = cmds.ikHandle(n=prefix + '_main_ikh',
                            sol='ikRPsolver',
                            sj=hand_joints[1],
                            ee=hand_joints[3]
                            )[0]

    # attach controls
    cmds.parentConstraint(body_attach_grp, pole_vector_ctrl.Off, mo=1)

    cmds.poleVectorConstraint(pole_vector_ctrl.C, hand_ik)
    if clavicle_joint:
        cmds.parentConstraint(base_attach_grp, clavicle_ctrl.Off, mo=1)

    # attach objects to controls
    cmds.parent(hand_ik, hand_ctrl.C)

    if clavicle_joint:
        cmds.parent(clavicle_ik, clavicle_ctrl.C)

    # make pole vector connection like
    pv_line_pose1 = cmds.xform(hand_joints[2], q=1, t=1, ws=1)
    pv_line_pose2 = cmds.xform(pole_vector_ctrl.C, q=1, t=1, ws=1)
    pole_vector_curve = cmds.curve(n=prefix + '_PV_curve', d=1, p=[pv_line_pose1, pv_line_pose2])
    cmds.cluster(pole_vector_curve + '.cv[0]',
                 n=prefix + '_pv1_cluster',
                 wn=[hand_joints[2], hand_joints[2]],
                 bs=True)
    cmds.cluster(pole_vector_curve + '.cv[1]',
                 n=prefix + '_pv1_cluster',
                 wn=[pole_vector_ctrl.C, pole_vector_ctrl.C],
                 bs=True)
    cmds.parent(pole_vector_curve, rig_module.controlsGrp)
    cmds.setAttr(pole_vector_curve + '.template', 1)
    cmds.setAttr(pole_vector_curve + '.it', 0)

    # creating finger FK controls
    finger_fk_constraints = []
    finger_fk_constraint_weights = []
    fk_finger_locators = []
    for top_finger_joint in top_finger_joints:
        listed_joints = joint.list_hierarchy(top_finger_joint, with_end_joints=False)
        finger_fk_loc = []
        for each in listed_joints:
            fk_finger_locator = control.Locator(prefix=each + '_FK_fingers',
                                                translate_to=each,
                                                rotate_to=each,
                                                scale=2,
                                                parent=hand_local_transform
                                                )
            finger_fk_loc.append(fk_finger_locator)
            fk_finger_locators.append(fk_finger_locator)
        for i, j in enumerate(listed_joints):
            print finger_fk_loc[i].L, j
            cmds.orientConstraint(finger_fk_loc[i].L, j, mo=1)
            fk_finger_ctrl_constraint = cmds.orientConstraint(finger_fk_loc[i].L, j, mo=1)
            fk_finger_ctrl_constraint_weight = cmds.orientConstraint(fk_finger_ctrl_constraint, q=True, wal=True)
            finger_fk_constraints.append(fk_finger_ctrl_constraint)
            finger_fk_constraint_weights.append(fk_finger_ctrl_constraint_weight)

        finger_length = len(finger_fk_loc)
        finger_fk_loc.reverse()
        if finger_fk_loc:
            for each in range(finger_length):
                if each <= finger_length - 2:
                    print each
                    cmds.parent(finger_fk_loc[each].L_Off, finger_fk_loc[each + 1].L)

    # creating finger IK controls
    finger_ik_control = []
    for top_finger_joint in top_finger_joints:
        finger_prefix = prefix + '_' + top_finger_joint
        finger_end_joint = cmds.listRelatives(top_finger_joint, ad=1, type='joint')[0]

        finger_ik_ctrl = control.Control(prefix=finger_prefix,
                                         translate_to=finger_end_joint,
                                         scale=rig_scale,
                                         parent=hand_local_transform,
                                         lock_channels=['t', 's'],
                                         shape='circleY'
                                         )

        finger_ik_control.append(finger_ik_ctrl)

    finger_ikh = []
    for i, top_finger_joint in enumerate(top_finger_joints):
        finger_prefix = prefix + top_finger_joint
        finger_joints = joint.list_hierarchy(top_finger_joint)

        finger_ik = cmds.ikHandle(n=finger_prefix + '_ikh',
                                  sol='ikSCsolver',
                                  sj=finger_joints[0],
                                  ee=finger_joints[-1]
                                  )[0]

        cmds.hide(finger_ik)
        cmds.parent(finger_ik, finger_ik_control[i].C)
        finger_ikh.append(finger_ik)

    # creating some fk constraint
    fk_hand_ctrl_constraint = cmds.orientConstraint(fk_hand_ctrl.C, hand_joints[3], mo=1)
    fk_hand_ctrl_constraint_weight = cmds.orientConstraint(fk_hand_ctrl_constraint, q=True, wal=True)

    hand_ctrl_constraint = cmds.orientConstraint(hand_ctrl.C, hand_joints[3], mo=1)
    hand_ctrl_constraint_weight = cmds.orientConstraint(hand_ctrl_constraint, q=True, wal=True)

    fk_shoulder_ctrl_constraint = cmds.orientConstraint(fk_shoulder_ctrl.L, hand_joints[1], mo=1)
    fk_shoulder_ctrl_constraint_weight = cmds.orientConstraint(fk_shoulder_ctrl_constraint, q=True, wal=True)

    fk_elbow_ctrl_constraint = cmds.orientConstraint(fk_elbow_ctrl.L, hand_joints[2], mo=1)
    fk_elbow_ctrl_constraint_weight = cmds.orientConstraint(fk_elbow_ctrl_constraint, q=True, wal=True)

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

    cmds.addAttr(ik_fk_switch_shape, longName='Hand_ik_fk_switch', defaultValue=1.0, minValue=0, maxValue=1, k=1)
    cmds.addAttr(ik_fk_switch_shape, longName='Finger_ik_fk_switch', defaultValue=1.0, minValue=0, maxValue=1, k=1)
    cmds.parent(ik_fk_switch_shape, hand_ctrl.C, add=True, shape=True)
    cmds.parent(ik_fk_switch_shape, fk_hand_ctrl.C, add=True, shape=True)

    # connecting FINGER, HAND and CLAVICLE IKH to IK_FK_switch
    for ikh in finger_ikh:
        cmds.connectAttr(ik_fk_switch_shape[0] + '.Finger_ik_fk_switch',
                         ikh + '.ikBlend')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     hand_ik + '.ikBlend')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     clavicle_ik + '.ikBlend')
    for i, constraint in enumerate(finger_fk_constraint_weights):
        cmds.connectAttr(ik_fk_switch_shape[0] + '.Finger_ik_fk_switch',
                         str(finger_fk_constraints[i][0]) + '.' + str(constraint[0]))

    # connecting CLAVICLE Constraint to IK_FK switch
    fk_clavicle_reverse_constraint = cmds.createNode('reverse', name='fk_clavicle_reverse_constraint')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     fk_clavicle_reverse_constraint + '.input.inputX')
    cmds.connectAttr(fk_clavicle_reverse_constraint + '.output.outputX',
                     fk_clavicle_ctrl_constraint[0] + '.' + fk_clavicle_ctrl_constraint_weight[0])

    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     clavicle_ctrl_constraint[0] + '.' + clavicle_ctrl_constraint_weight[1])

    # connecting SHOULDER Constraint to IK_FK switch
    shoulder_reverse_node = cmds.createNode('reverse', name='shoulder_reverse')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     shoulder_reverse_node + '.input.inputX')

    # connecting ELBOW Constraint to IK_FK switch
    elbow_reverse_node = cmds.createNode('reverse', name='elbow_reverse')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     elbow_reverse_node + '.input.inputX')
    cmds.connectAttr(elbow_reverse_node + '.output.outputX',
                     fk_elbow_ctrl_constraint[0] + '.' + fk_elbow_ctrl_constraint_weight[0])

    # connecting HAND Constraint to IK_FK switch
    fk_hand_reverse_constraint = cmds.createNode('reverse', name='fk_hand_reverse_constraint')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     fk_hand_reverse_constraint + '.input.inputX')
    cmds.connectAttr(fk_hand_reverse_constraint + '.output.outputX',
                     fk_hand_ctrl_constraint[0] + '.' + fk_hand_ctrl_constraint_weight[0])

    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     hand_ctrl_constraint[0] + '.' + hand_ctrl_constraint_weight[1])

    # connecting control VISIBILITY
    # connecting FK visibility
    hand_visibility_reverse_node = cmds.createNode('reverse', name='hand_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     hand_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(hand_visibility_reverse_node + '.output.outputX',
                     fk_hand_ctrl.C + '.v')
    
    elbow_visibility_reverse_node = cmds.createNode('reverse', name='elbow_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     elbow_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(elbow_visibility_reverse_node + '.output.outputX',
                     fk_elbow_ctrl.L + '.v')
    
    shoulder_visibility_reverse_node = cmds.createNode('reverse', name='shoulder_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     shoulder_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(shoulder_visibility_reverse_node + '.output.outputX',
                     fk_shoulder_ctrl.L + '.v')

    clavicle_visibility_reverse_node = cmds.createNode('reverse', name='clavicle_visibility_reverse_node')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     clavicle_visibility_reverse_node + '.input.inputX')
    cmds.connectAttr(clavicle_visibility_reverse_node + '.output.outputX',
                     fk_clavicle_ctrl.L + '.v')
    
    # connecting IK visibility
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     hand_ctrl.C + '.v')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Hand_ik_fk_switch',
                     clavicle_ctrl.C + '.v')

    # connecting finger visibility
    for finger_ik in finger_ik_control:
        cmds.connectAttr(ik_fk_switch_shape[0] + '.Finger_ik_fk_switch',
                         finger_ik.C + '.v')
    fk_finger_reverse_node = cmds.createNode('reverse', name='finger_fk_reverse')
    cmds.connectAttr(ik_fk_switch_shape[0] + '.Finger_ik_fk_switch',
                     fk_finger_reverse_node + '.input.inputX')
    for fk_loc in fk_finger_locators:
        cmds.connectAttr(fk_finger_reverse_node + '.output.outputX',
                         fk_loc.L + '.v')

    return {'module': rig_module,
            'base_attach_grp': base_attach_grp,
            'body_attach_grp': body_attach_grp,
            'hand_ctrl': hand_ctrl
            }
