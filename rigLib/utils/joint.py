"""
joint utils @ utils
"""

from maya import cmds


def list_hierarchy(top_joint, with_end_joints=True):
    """
    list joint hierarchy staring with top group
    :param top_joint: str, joint to get listed with its joint hierarchy
    :param with_end_joints: bool, list hierarchy including end joints
    :return: list(str), listed joints started
    """

    listed_joints = cmds.listRelatives(top_joint, type='joint', ad=True)
    listed_joints.append(top_joint)
    listed_joints.reverse()

    complete_joints = listed_joints[:]

    if not with_end_joints:
        complete_joints = [j for j in listed_joints if cmds.listRelatives(j, c=1, type='joint')]

    return complete_joints
