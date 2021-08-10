"""
spine @rig
"""
from maya import cmds
from rigLib.base import module
from rigLib.base import control


def build(spine_joints,
          root_joints,
          spine_curve,
          body_locator,
          chest_locator,
          pelvis_locator,
          prefix='spine',
          rig_scale=1.0,
          base_rig=None
          ):
    """
    :param spine_joints: list( string values ), list of 6 spine joints
    :param root_joints: str, root
    :param spine_curve: str, name of spine cubic curve with 5 cv's. matching
    first 5 joints
    :param body_locator: str reference transform of body control
    :param chest_locator: str reference transform of chest control
    :param pelvis_locator: str reference transform of pelvis control
    :param prefix: str, prefix name to new object
    :param rig_scale: float, scale factor for size of controls
    :param base_rig: instance of base module base class
    :return: dictionary with rig module objects
    """

    # make rig module
    rig_module = module.Module(prefix=prefix, base_object=base_rig)

    # make spine curve clusters
    spine_curve_cvs = cmds.ls(spine_curve + '.cv[*]', fl=1)
    number_of_spine_cv = len(spine_curve_cvs)
    spine_curve_clusters = []

    for i in range(number_of_spine_cv):
        cls = cmds.cluster(spine_curve_cvs[i], n=prefix + '_Cluster %d' % (i + 1))
        spine_curve_clusters.append(cls[1])

    cmds.hide(spine_curve_clusters)

    # parent spine curve
    cmds.parent(spine_curve, rig_module.partsNoTransGrp)

    # make controls
    body_control = control.Control(prefix=prefix + '_Body',
                                   translate_to=pelvis_locator,
                                   scale=rig_scale * 25,
                                   parent=rig_module.controlsGrp,
                                   shape='circleY')

    chest_control = control.Control(prefix=prefix + '_Chest',
                                    translate_to=chest_locator,
                                    scale=rig_scale * 20,
                                    parent=body_control.C,
                                    shape='circleY')

    pelvis_control = control.Control(prefix=prefix + '_Pelvis',
                                     translate_to=pelvis_locator,
                                     scale=rig_scale * 17,
                                     parent=body_control.C,
                                     shape='circleY')

    middle_control = control.Control(prefix=prefix + '_Middle',
                                     translate_to=spine_curve_clusters[3],
                                     scale=rig_scale * 17,
                                     parent=body_control.C,
                                     lock_channels=['r', 's', 'v'],
                                     shape='circleY')

    _adjust_control_shape(body_control, spine_joints, rig_scale)

    cmds.parentConstraint(chest_control.C, pelvis_control.C, middle_control.Off, sr=['x', 'y', 'z'], mo=1)

    # attach clusters
    middle_spine_cv = int(len(spine_curve_cvs) / 2)
    cmds.parent(spine_curve_clusters[middle_spine_cv + 1:], chest_control.C)
    cmds.parent(spine_curve_clusters[middle_spine_cv], middle_control.C)
    cmds.parent(spine_curve_clusters[:middle_spine_cv], pelvis_control.C)

    # attach chest joint
    # cmds.orientConstraint(chest_control.C, spine_joints[-1], mo=1)

    # creating spine kf controls
    spine_fk_loc = []
    spine_joints = cmds.ls('spine*', type='joint')
    for spine_joint in spine_joints:
        fk_spine_locator = control.Locator(prefix=spine_joint + '_FK_spines',
                                           translate_to=spine_joint,
                                           rotate_to=spine_joint,
                                           scale=2,
                                           parent=body_control.C
                                           )
        spine_fk_loc.append(fk_spine_locator)

    spine_length = len(spine_fk_loc)
    spine_fk_loc.reverse()
    if spine_fk_loc:
        for each in range(spine_length):
            if each <= spine_length - 2:
                print each
                cmds.parent(spine_fk_loc[each].L_Off, spine_fk_loc[each + 1].L)

    # attaching FK controls
    spine_fk_loc.reverse()
    for i, j in enumerate(spine_joints):
        cmds.parentConstraint(spine_fk_loc[i].L, j, mo=1)

    # make IK handle
    spine_ik = cmds.ikHandle(n=prefix + '_ikh',
                             sol='ikSplineSolver',
                             sj=spine_joints[0],
                             ee=spine_joints[-1],
                             c=spine_curve,
                             ccv=0,
                             parentCurve=0)[0]

    cmds.hide(spine_ik)
    cmds.parent(spine_ik, rig_module.partsNoTransGrp)

    # setup IK twist
    cmds.setAttr(spine_ik + '.dTwistControlEnable', 1)
    cmds.setAttr(spine_ik + '.dWorldUpType', 4)
    cmds.setAttr(spine_ik + '.dForwardAxis', 2)
    cmds.setAttr(spine_ik + '.dWorldUpAxis', 3)
    cmds.setAttr(spine_ik + '.dWorldUpVectorY', 0)
    cmds.setAttr(spine_ik + '.dWorldUpVectorZ', 1)
    cmds.setAttr(spine_ik + '.dWorldUpVectorEndY', 0)
    cmds.setAttr(spine_ik + '.dWorldUpVectorEndZ', 1)
    cmds.connectAttr(chest_control.C + '.worldMatrix[0]', spine_ik + '.dWorldUpMatrixEnd')
    cmds.connectAttr(pelvis_control.C + '.worldMatrix[0]', spine_ik + '.dWorldUpMatrix')

    # attach root joint
    cmds.parentConstraint(pelvis_control.C, root_joints, mo=1)

    # attaching neck to chest

    # parent FK joints to IK
    cmds.parentConstraint(spine_fk_loc[-1].L, chest_control.Off)

    return {'module': rig_module,
            'body_control': body_control,
            'chest_control': chest_control,
            'last_fk_spine': spine_fk_loc[-1].L}


def _adjust_control_shape(body_control, spine_joints, rig_scale):
    """
    offset body control along the y axis
    :param body_control:
    :param spine_joints:
    :param rig_scale:
    :return:
    """

    offset_grp = cmds.group(em=1, p=body_control.C)

    cmds.parent(offset_grp, spine_joints[2])

    control_cluster = cmds.cluster(cmds.listRelatives(body_control.C, s=1))[1]
    cmds.parent(control_cluster, offset_grp)

    cmds.move(10 * rig_scale, offset_grp, moveY=1, relative=1, objectSpace=1)
    cmds.delete(body_control.C, ch=1)
