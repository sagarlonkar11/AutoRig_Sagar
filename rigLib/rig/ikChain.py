"""
ikChain @ rig
"""
from maya import cmds
from rigLib.base import module
from rigLib.base import control


def build(chain_joints,
          chain_curve,
          prefix='tail',
          rig_scale=1,
          smallest_scale_precentage=0.5,
          fk_parenting=True,
          base_rig=None
          ):
    """

    :param chain_joints: list(str), list of chain joints
    :param chain_curve: str, name of chain cubic curve
    :param prefix: str, prefix to name new objects
    :param rig_scale: float, scale factor for size of controls
    :param smallest_scale_precentage: float, scale of smallest control at the end of chain
            compaired to rig scale
    :param fk_parenting: bool, parent each control to previous one make FK chain
    :param base_rig: instance of base, module, base class
    :return: dictionary with rig module objects
    """
    # make rig module

    rig_module = module.Module(prefix=prefix, base_object=base_rig)

    # make chain curve clusters

    chain_curve_cvs = cmds.ls(chain_curve + '.cv[*]', fl=1)
    number_of_chain_cv = len(chain_curve_cvs)
    chain_curve_clusters = []
    for i in range(number_of_chain_cv):
        cls = cmds.cluster(chain_curve_cvs[i], n=prefix + 'cluster%d' % (i + 1))[1]
        chain_curve_clusters.append(cls)

    cmds.hide(chain_curve_clusters)

    # parent chain curve
    cmds.parent(chain_curve, rig_module.partsNoTransGrp)

    # make attach grps

    base_attach_grp = cmds.group(n=prefix + 'base_attach_grp', em=1, p=rig_module.partsGrp)
    cmds.delete(cmds.pointConstraint(chain_joints[0], base_attach_grp))

    # make controls

    chain_controls = []

    control_scale_increment = (1.0 - smallest_scale_precentage) / number_of_chain_cv
    main_control_scale_factor = 5.0

    for i in range(number_of_chain_cv):
        control_scale = rig_scale * main_control_scale_factor * (1.0 - (i * control_scale_increment))
        ctrl = control.Control(prefix=prefix + '%d' % (i + 1),
                               translate_to=chain_curve_clusters[i],
                               scale=control_scale,
                               parent=rig_module.controlsGrp,
                               shape='sphere'
                               )
        chain_controls.append(ctrl)

    # parent controls
    if fk_parenting:
        for i in range(number_of_chain_cv):
            if i == 0:
                continue
            cmds.parent(chain_controls[i].Off, chain_controls[i-1].C)

    # attach clusters
    for i in range(number_of_chain_cv):
        cmds.parent(chain_curve_clusters[i], chain_controls[i].C)

    # attach controls
    cmds.parentConstraint(base_attach_grp, chain_controls[0].Off, mo=1)

    # make IK handle
    chain_ik = cmds.ikHandle(n=prefix + '_ikh',
                             sol='ikSplineSolver',
                             sj=chain_joints[0],
                             ee=chain_joints[-1],
                             c=chain_curve,
                             ccv=0,
                             parentCurve=0
                             )[0]

    cmds.hide(chain_ik)
    cmds.parent(chain_ik, rig_module.partsNoTransGrp)

    # add twist attribute

    twist_attribute = 'twist'

    cmds.addAttr(chain_controls[-1].C, ln=twist_attribute, k=1)
    cmds.connectAttr(chain_controls[-1].C + '.' + twist_attribute, chain_ik + '.twist')

    return {'module': rig_module,
            'base_attach_grp': base_attach_grp
            }
