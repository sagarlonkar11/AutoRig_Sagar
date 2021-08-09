'''
Main module for Human rig setup
deformation set up
'''
# from . import project
import humanRig
import rigLib
from maya import cmds
from maya import mel

top_joint = 'root'
skin_weights_dir = 'weights/skinCluster'
save_weights_ext = '.weightMap'
body_geo = 'Body'
body_mid_res_geo = 'Body_highRes'


def build(base_rig, character_name):
    model_grp = '%s_model_grp' % character_name

    # make Twist Joints
    'TODO: do not hard code'
    # old list ['LeftForeArm', 'LeftLeg', 'RightForeArm', 'RightLeg']
    ref_twist_joints = cmds.ls(('*_elbow*', '*_knee*'), type='joint')
    make_twist_joints(base_rig, ref_twist_joints)

    # get Model Update
    geo_list = _get_model_geo_update(model_grp)

    # apply skinCluster
    apply_skin_cluster(geo_list)

    # load skin Cluster
    # load_skin_weights(geo_list)

    # apply mush deformer
    # _apply_delta_mesh(body_geo)

    # wrap highref mesh
    # _make_wrap(body_mid_res_geo, body_geo)

    pass


def _make_wrap(wrap_objects, wrapper_objects):
    cmds.select(wrap_objects)
    cmds.select(wrapper_objects, add=1)
    mel.eval('doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" }')
    # using alternate method
    # cmds.deformer(type='wrap')


def _apply_delta_mesh(geo):
    delta_mesh_DF = cmds.deltaMush(geo, smoothingIterations=50, smoothingStep=0.8)[0]


def _get_model_geo_update(model_grp):
    geo_list = [cmds.listRelatives(o, p=1)[0] for o in cmds.listRelatives(model_grp, ad=1, type='mesh')]

    return geo_list


def make_twist_joints(base_rig, parent_joints):
    twist_joints_main_grp = cmds.group(n='twist_joint_grp', p=base_rig.jointsGrp, em=1)

    for parentJoint in parent_joints:
        # prefix = rigLib.utils.name.remove_suffix(parentJoint)
        prefix = parentJoint
        # prefix = prefix[:-1]

        parent_joint_child = cmds.listRelatives(parentJoint, c=1, type='joint')[0]

        # make twist joints

        twist_joints_grp = cmds.group(n=prefix + 'twistJoint_grp', p=twist_joints_main_grp, em=1)

        twist_parent_joint = cmds.duplicate(parentJoint, n=prefix + 'twist_jt', parentOnly=True)[0]
        twist_child_joint = cmds.duplicate(parent_joint_child, n=prefix + 'twist2_jt', parentOnly=True)[0]

        # adjust twistJoints

        original_joint_radius = cmds.getAttr(parentJoint + '.radius')

        for j in [twist_parent_joint, twist_child_joint]:
            cmds.setAttr(j + '.radius', original_joint_radius * 2)
            cmds.color(j, ud=1)

        cmds.parent(twist_child_joint, twist_parent_joint)
        cmds.parent(twist_parent_joint, twist_joints_grp)

        # attaching twist joints

        cmds.pointConstraint(parentJoint, twist_parent_joint)

        # make IK handle

        twist_ik = cmds.ikHandle(n=prefix + '_twist_joint_ikh',
                                 sol='ikSCsolver',
                                 sj=twist_parent_joint,
                                 ee=twist_child_joint)[0]
        cmds.hide(twist_ik)
        cmds.parent(twist_ik, twist_joints_grp)
        cmds.parentConstraint(parent_joint_child, twist_ik)


def apply_skin_cluster(geo_list):
    skin_joints = rigLib.utils.joint.list_hierarchy(top_joint, with_end_joints=False)

    fk_joints = cmds.ls('fk_*', type='joint')
    for each in fk_joints:
        if each in skin_joints:
            skin_joints.remove(str(each))

    for mesh in geo_list:
        cmds.skinCluster(mesh, skin_joints, tsb=True, omi=True, dr=4.5, removeUnusedInfluence=True)


def save_skin_weights():
    """
    Save weights for character geomety objects
    """
    # weight file
    # weight_files = os.path.join(project.project_path, character_name,skin_weights_dir, objects + save_weights_ext)

    # skinWeight file save
    mel.eval('$obj =`ls -sl`;performExportSkinMap 1;')


def load_skin_weights(geo_list):
    """
    Save weights for character geomety objects
    """
    for mesh in geo_list:
        print 'please load skin weights of ' + mesh
        cmds.select(mesh)
        mel.eval('$obj =`ls -sl`;ImportSkinWeightMaps 1')
