"""
transform @ utils

Functions to manipulate and create transforms
"""

from maya import cmds
from . import name


def make_offset_grp(object, prefix=''):
    """
    Make offset grp to the given object
    :param object: transform object to get offset grp
    :param prefix: str, prefix to name new object
    :return: str, name of new offset grp
    """

    if not prefix:
        prefix = name.remove_suffix(object)

    offset_grp = cmds.group(n=prefix + 'offset_grp', em=1)

    object_parents = cmds.listRelatives(object, p=1)

    if object_parents:
        cmds.parent(offset_grp, object_parents[0])

    cmds.delete(cmds.parentConstraint(object, offset_grp))
    cmds.delete(cmds.scaleConstraint(object, offset_grp))

    # parent object under the offset grps

    cmds.parent(object, offset_grp)

    return offset_grp
