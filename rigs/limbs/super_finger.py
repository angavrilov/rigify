import bpy
import re
from ...utils import copy_bone, flip_bone
from ...utils import strip_org, make_deformer_name, connected_children_names, make_mechanism_name
from ...utils import create_circle_widget, create_widget, create_sphere_widget
from ...utils import MetarigError, align_bone_x_axis
from ...utils import layout_layer_selection_ui
from .limb_utils import get_bone_name
from mathutils   import Vector
from rna_prop_ui import rna_idprop_ui_prop_get

script_header = """
controls    = [%s]
if is_selected(controls):
"""

script_prop = """
    layout.prop(pose_bones['%s'], '["%s"]', text="%s", slider=True)
"""

script_prop_switch = """
    layout.prop(pose_bones['%s'], '["%s"]', text="%s", slider=False)
"""

script_ik2fk = """
    props = layout.operator("pose.rigify_finger_ik2fk_" + rig_id, text="Snap IK->FK (%s)")
    props.ik_ctl = '%s'
    props.fk_ctl = '%s'
"""

script_fk2ik = """
    props = layout.operator("pose.rigify_finger_fk2ik_" + rig_id, text="Snap FK->Act (%s)")
    props.fk_master = '%s'
    props.fk_master_drv = str([%s])
    props.fk_controls = str([%s])
    props.fk_chain = str([%s])
    props.ik_chain = str([%s])
    props.axis = '%s'
"""

script_fk2ik_norm = """
    props = layout.operator("pose.rigify_finger_fk2ik_" + rig_id, text="Normalize (%s)")
    props.fk_master = '%s'
    props.fk_master_drv = str([%s])
    props.fk_controls = str([%s])
    props.axis = '%s'
"""


class Rig:

    def __init__(self, obj, bone_name, params):
        self.obj = obj
        self.org_bones = [bone_name] + connected_children_names(obj, bone_name)
        self.params = params

        if params.tweak_extra_layers:
            self.tweak_layers = list(params.tweak_layers)
        else:
            self.tweak_layers = None

        if params.ik_extra_layers:
            self.ik_layers = list(params.ik_layers)
        else:
            self.ik_layers = None

        if len(self.org_bones) <= 1:
            raise MetarigError("RIGIFY ERROR: Bone '%s': listen bro, that finger rig jusaint put tugetha rite. A little hint, use more than one bone!!" % (strip_org(bone_name)))

        if params.generate_ik and params.ik_parent_bone != '':
            if get_bone_name(params.ik_parent_bone, 'org') not in obj.data.bones:
                raise MetarigError("RIGIFY ERROR: Bone '%s': IK parent '%s' not found." % (strip_org(bone_name), params.ik_parent_bone))


    def orient_org_bones(self):

        bpy.ops.object.mode_set(mode='EDIT')
        eb = self.obj.data.edit_bones

        if self.params.primary_rotation_axis == 'automatic':

            first_bone = eb[self.org_bones[0]]
            last_bone = eb[self.org_bones[-1]]

            # Orient uarm farm bones
            chain_y_axis = last_bone.tail - first_bone.head
            chain_rot_axis = first_bone.y_axis.cross(chain_y_axis)  # ik-plane normal axis (rotation)
            if chain_rot_axis.length < first_bone.length/100:
                chain_rot_axis = first_bone.x_axis.normalized()
            else:
                chain_rot_axis = chain_rot_axis.normalized()

            for bone in self.org_bones:
                align_bone_x_axis(self.obj, bone, chain_rot_axis)

    def generate(self):
        org_bones = self.org_bones

        bpy.ops.object.mode_set(mode='EDIT')
        eb = self.obj.data.edit_bones

        self.orient_org_bones()

        # Bone name lists
        ctrl_chain = []
        def_chain = []
        mch_chain = []
        mch_drv_chain = []

        # Create ctrl master bone
        org_name = self.org_bones[0]
        temp_name = strip_org(self.org_bones[0])

        # Compute master bone name: inherit .LR suffix, but strip trailing digits
        name_parts = re.match(r'^(.*?)(?:([._-])?\d+)?((?:[._-][LlRr])?)(?:\.\d+)?$', temp_name)
        name_base, name_sep, name_suffix = name_parts.groups()
        name_base += name_sep if name_sep else '_'

        master_name = copy_bone(self.obj, org_name, name_base + 'master' + name_suffix)
        ctrl_bone_master = eb[master_name]

        # Parenting bug fix ??
        ctrl_bone_master.use_connect = False
        ctrl_bone_master.parent = None

        ctrl_bone_master.tail += (eb[org_bones[-1]].tail - eb[org_name].head) * 1.25

        for bone in org_bones:
            eb[bone].use_connect = False
            if org_bones.index(bone) != 0:
                eb[bone].parent = None

        # Creating the bone chains
        for i in range(len(self.org_bones)):

            name = self.org_bones[i]
            ctrl_name = strip_org(name)

            # Create control bones
            ctrl_bone = copy_bone(self.obj, name, ctrl_name)
            ctrl_bone_e = eb[ctrl_name]

            # Create deformation bones
            def_name = make_deformer_name(ctrl_name)
            def_bone = copy_bone(self.obj, name, def_name)

            # Create mechanism bones
            mch_name = make_mechanism_name(ctrl_name)
            mch_bone = copy_bone(self.obj, name, mch_name)

            # Create mechanism driver bones
            drv_name = make_mechanism_name(ctrl_name) + "_drv"
            mch_bone_drv = copy_bone(self.obj, name, drv_name)

            # Adding to lists
            ctrl_chain += [ctrl_bone]
            def_chain += [def_bone]
            mch_chain += [mch_bone]
            mch_drv_chain += [mch_bone_drv]

        # Creating tip control bone
        tip_name = copy_bone(self.obj, org_bones[-1], name_base + 'tip' + name_suffix)
        ctrl_bone_tip = eb[tip_name]
        flip_bone(self.obj, tip_name)
        ctrl_bone_tip.length /= 2

        ctrl_bone_tip.parent = eb[ctrl_chain[-1]]

        # Create IK control bone and follow socket
        if self.params.generate_ik:
            ik_ctrl_name = copy_bone(self.obj, tip_name, name_base + 'ik' + name_suffix)
            ik_ctrl_bone = eb[ik_ctrl_name]
            ik_ctrl_bone.tail = ik_ctrl_bone.head + Vector((0, ik_ctrl_bone.length * 1.5, 0))
            ik_ctrl_bone.roll = 0

            if eb[org_name].parent or self.params.ik_parent_bone != '':
                ik_socket_name = copy_bone(self.obj, org_name, get_bone_name(org_name, 'mch', 'ik_socket'))
                ik_socket_bone = eb[ik_socket_name]
                ik_socket_bone.length *= 0.8;
                ik_socket_bone.parent = None

                eb[ik_ctrl_name].parent = ik_socket_bone

                ik_parent_name = copy_bone(self.obj, org_name, get_bone_name(org_name, 'mch', 'ik_parent'))
                ik_parent_bone = eb[ik_parent_name]
                ik_parent_bone.length *= 0.7;

                if self.params.ik_parent_bone != '':
                    ik_parent_bone.parent = eb[get_bone_name(self.params.ik_parent_bone, 'org')]
            else:
                ik_socket_name = None
                ik_ctrl_bone.parent = None

        # Restoring org chain parenting
        for bone in org_bones[1:]:
            eb[bone].parent = eb[org_bones[org_bones.index(bone) - 1]]
            eb[bone].use_connect = True

        # Parenting the master bone parallel to the first org
        ctrl_bone_master = eb[master_name]
        ctrl_bone_master.parent = eb[org_bones[0]].parent

        # Parenting chain bones
        for i in range(len(self.org_bones)):
            # Edit bone references
            def_bone_e = eb[def_chain[i]]
            ctrl_bone_e = eb[ctrl_chain[i]]
            mch_bone_e = eb[mch_chain[i]]
            mch_bone_drv_e = eb[mch_drv_chain[i]]

            if i == 0:
                # First ctl bone
                ctrl_bone_e.parent = mch_bone_drv_e
                ctrl_bone_e.use_connect = False
                # First def bone
                def_bone_e.parent = eb[self.org_bones[i]].parent
                def_bone_e.use_connect = False
                # First mch bone
                mch_bone_e.parent = ctrl_bone_e
                mch_bone_e.use_connect = False
                # First mch driver bone
                mch_bone_drv_e.parent = eb[self.org_bones[i]].parent
                mch_bone_drv_e.use_connect = False
            else:
                # The rest
                ctrl_bone_e.parent = mch_bone_drv_e
                ctrl_bone_e.use_connect = False

                def_bone_e.parent = eb[def_chain[i-1]]
                def_bone_e.use_connect = True

                mch_bone_drv_e.parent = eb[ctrl_chain[i-1]]
                mch_bone_drv_e.use_connect = False

                # Parenting mch bone
                mch_bone_e.parent = ctrl_bone_e
                mch_bone_e.use_connect = False

        bpy.ops.object.mode_set(mode='OBJECT')

        pb = self.obj.pose.bones

        # Setting pose bones locks
        pb_master = pb[master_name]
        pb_master.lock_scale = True, False, True

        pb[tip_name].lock_scale = True, True, True
        pb[tip_name].lock_rotation = True, True, True
        pb[tip_name].lock_rotation_w = True

        pb_master['finger_curve'] = 0.0
        prop = rna_idprop_ui_prop_get(pb_master, 'finger_curve')
        prop["min"] = 0.0
        prop["max"] = 1.0
        prop["soft_min"] = 0.0
        prop["soft_max"] = 1.0
        prop["description"] = "Rubber hose finger cartoon effect"

        # Pose settings
        for org, ctrl, deform, mch, mch_drv in zip(self.org_bones, ctrl_chain, def_chain, mch_chain, mch_drv_chain):
            # Constraining the org bones
            con = pb[org].constraints.new('COPY_TRANSFORMS')
            con.target = self.obj
            con.subtarget = mch

            # Constraining the deform bones
            if deform == def_chain[0]:
                con = pb[deform].constraints.new('COPY_LOCATION')
                con.target = self.obj
                con.subtarget = org

                con = pb[deform].constraints.new('COPY_SCALE')
                con.target = self.obj
                con.subtarget = org

                con = pb[deform].constraints.new('DAMPED_TRACK')
                con.target = self.obj
                con.subtarget = org_bones[1]

                con = pb[deform].constraints.new('STRETCH_TO')
                con.target = self.obj
                con.subtarget = org_bones[1]
                con.volume = 'NO_VOLUME'
            else:
                con = pb[deform].constraints.new('COPY_TRANSFORMS')
                con.target = self.obj
                con.subtarget = org

            # Constraining the mch bones
            if mch_chain.index(mch) == len(mch_chain) - 1:
                con = pb[mch].constraints.new('DAMPED_TRACK')
                con.target = self.obj
                con.subtarget = tip_name

                con = pb[mch].constraints.new('STRETCH_TO')
                con.target = self.obj
                con.subtarget = tip_name
                con.volume = 'NO_VOLUME'
            else:
                con = pb[mch].constraints.new('DAMPED_TRACK')
                con.target = self.obj
                con.subtarget = ctrl_chain[ctrl_chain.index(ctrl)+1]

                con = pb[mch].constraints.new('STRETCH_TO')
                con.target = self.obj
                con.subtarget = ctrl_chain[ctrl_chain.index(ctrl)+1]
                con.volume = 'NO_VOLUME'

            # Constraining and driving mch driver bones
            pb[mch_drv].rotation_mode = 'YZX'

            if mch_drv_chain.index(mch_drv) == 0:
                # Constraining to master bone
                con = pb[mch_drv].constraints.new('COPY_LOCATION')
                con.target = self.obj
                con.subtarget = master_name

                con = pb[mch_drv].constraints.new('COPY_ROTATION')
                con.target = self.obj
                con.subtarget = master_name
                con.target_space = 'LOCAL'
                con.owner_space = 'LOCAL'

            else:
                # Match axis to expression
                options = {
                    "automatic": {"axis": 0,
                                  "expr": '(1-sy)*pi'},
                    "X": {"axis": 0,
                          "expr": '(1-sy)*pi'},
                    "-X": {"axis": 0,
                           "expr": '-((1-sy)*pi)'},
                    "Y": {"axis": 1,
                          "expr": '(1-sy)*pi'},
                    "-Y": {"axis": 1,
                           "expr": '-((1-sy)*pi)'},
                    "Z": {"axis": 2,
                          "expr": '(1-sy)*pi'},
                    "-Z": {"axis": 2,
                           "expr": '-((1-sy)*pi)'}
                }

                axis = self.params.primary_rotation_axis

                # Drivers
                drv = pb[mch_drv].driver_add("rotation_euler", options[axis]["axis"]).driver
                drv.type = 'SCRIPTED'
                drv.expression = options[axis]["expr"]
                drv_var = drv.variables.new()
                drv_var.name = 'sy'
                drv_var.type = "SINGLE_PROP"
                drv_var.targets[0].id = self.obj
                drv_var.targets[0].data_path = pb[master_name].path_from_id() + '.scale.y'

                if self.params.generate_ik:
                    stiffness = [0.99, 0.99, 0.99]
                    stiffness[options[axis]["axis"]] = 0.0
                    pb[org].ik_stiffness_x, pb[org].ik_stiffness_y, pb[org].ik_stiffness_z = stiffness

            # Setting bone curvature setting, custom property, and drivers
            def_bone = self.obj.data.bones[deform]

            def_bone.bbone_segments = 8
            drv = def_bone.driver_add("bbone_in").driver    # Ease in

            drv.type='SUM'
            drv_var = drv.variables.new()
            drv_var.name = "curvature"
            drv_var.type = "SINGLE_PROP"
            drv_var.targets[0].id = self.obj
            drv_var.targets[0].data_path = pb_master.path_from_id() + '["finger_curve"]'

            drv = def_bone.driver_add("bbone_out").driver   # Ease out

            drv.type='SUM'
            drv_var = drv.variables.new()
            drv_var.name = "curvature"
            drv_var.type = "SINGLE_PROP"
            drv_var.targets[0].id = self.obj
            drv_var.targets[0].data_path = pb_master.path_from_id() + '["finger_curve"]'

            # Assigning shapes to control bones
            create_circle_widget(self.obj, ctrl, radius=0.3, head_tail=0.5)

            if self.tweak_layers:
                pb[ctrl].bone.layers = self.tweak_layers

        # Generate IK constraints, drivers and widget
        if self.params.generate_ik:
            pb_ik_ctrl = pb[ik_ctrl_name]
            pb_ik_ctrl.lock_scale = True, True, True
            pb_ik_ctrl.lock_rotation = True, True, True
            pb_ik_ctrl.lock_rotation_w = True

            pb_ik_ctrl['IK_FK'] = 1.0
            prop = rna_idprop_ui_prop_get(pb_ik_ctrl, 'IK_FK')
            prop["min"] = prop["soft_min"] = 0.0
            prop["max"] = prop["soft_max"] = 1.0
            prop["description"] = 'IK/FK Switch'

            if ik_socket_name:
                pb_ik_ctrl['IK_follow'] = 1
                prop = rna_idprop_ui_prop_get(pb_ik_ctrl, 'IK_follow')
                prop["min"] = prop["soft_min"] = 0
                prop["max"] = prop["soft_max"] = 1
                prop["description"] = 'IK follows parent'

            # widget
            create_sphere_widget(self.obj, ik_ctrl_name)

            if self.ik_layers:
                pb_ik_ctrl.bone.layers = self.ik_layers

            # ik constraint
            con = pb[org_bones[-1]].constraints.new('IK')
            con.target = self.obj
            con.subtarget = ik_ctrl_name
            con.chain_count = len(org_bones)

            drv_fcu = con.driver_add("influence")
            drv = drv_fcu.driver
            drv.type = 'SUM'
            drv_var = drv.variables.new()
            drv_var.name = 'ik_fk'
            drv_var.type = 'SINGLE_PROP'
            drv_var.targets[0].id = self.obj
            drv_var.targets[0].data_path = pb_ik_ctrl.path_from_id() + '["IK_FK"]'

            mod = drv_fcu.modifiers[0]
            mod.poly_order = 1
            mod.coefficients[0] = 1.0
            mod.coefficients[1] = -1.0

            # follow parent constraint
            if ik_socket_name:
                con = pb[ik_socket_name].constraints.new('COPY_TRANSFORMS')
                con.target = self.obj
                con.subtarget = ik_parent_name

                drv = con.driver_add("influence").driver
                drv.type = 'SUM'
                drv_var = drv.variables.new()
                drv_var.name = 'IK_follow'
                drv_var.type = 'SINGLE_PROP'
                drv_var.targets[0].id = self.obj
                drv_var.targets[0].data_path = pb_ik_ctrl.path_from_id() + '["IK_follow"]'

        # Create ctrl master widget
        w = create_widget(self.obj, master_name)
        if w is not None:
            mesh = w.data
            verts = [(0, 0, 0), (0, 1, 0), (0.05, 1, 0), (0.05, 1.1, 0), (-0.05, 1.1, 0), (-0.05, 1, 0)]
            if 'Z' in self.params.primary_rotation_axis:
                # Flip x/z coordinates
                temp = []
                for v in verts:
                    temp += [(v[2], v[1], v[0])]
                verts = temp
            edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 1)]
            mesh.from_pydata(verts, edges, [])
            mesh.update()

        # Create tip control widget
        create_circle_widget(self.obj, tip_name, radius=0.3, head_tail=0.0)

        if self.tweak_layers:
            pb[tip_name].bone.layers = self.tweak_layers

        # Create UI
        controls = ctrl_chain + [tip_name, master_name]
        if self.params.generate_ik:
            controls.append(ik_ctrl_name)

        controls_string = ", ".join(["'" + x + "'" for x in controls])
        script = script_header % (controls_string)
        script += script_prop % (master_name, 'finger_curve', 'Curvature')

        if self.params.generate_ik:
            script += script_prop % (ik_ctrl_name, 'IK_FK', 'IK/FK')
            if ik_socket_name:
                script += script_prop_switch % (ik_ctrl_name, 'IK_follow', 'IK follow')
            script += script_ik2fk % (temp_name, ik_ctrl_name, tip_name)
            script += script_fk2ik % (
                temp_name, master_name,
                ", ".join(["'" + x + "'" for x in mch_drv_chain]),
                ", ".join(["'" + x + "'" for x in ctrl_chain]),
                ", ".join(["'" + x + "'" for x in mch_chain]),
                ", ".join(["'" + x + "'" for x in org_bones]),
                self.params.primary_rotation_axis
                )
        else:
            script += script_fk2ik_norm % (
                temp_name, master_name,
                ", ".join(["'" + x + "'" for x in mch_drv_chain]),
                ", ".join(["'" + x + "'" for x in ctrl_chain]),
                self.params.primary_rotation_axis
                )

        return [script]


def add_parameters(params):
    """ Add the parameters of this rig type to the
        RigifyParameters PropertyGroup
    """
    items = [('automatic', 'Automatic', ''), ('X', 'X manual', ''), ('Y', 'Y manual', ''), ('Z', 'Z manual', ''),
             ('-X', '-X manual', ''), ('-Y', '-Y manual', ''), ('-Z', '-Z manual', '')]
    params.primary_rotation_axis = bpy.props.EnumProperty(items=items, name="Primary Rotation Axis", default='automatic')

    # Setting up extra tweak layers
    params.tweak_extra_layers = bpy.props.BoolProperty(
        name="tweak_extra_layers",
        default=False,
        description=""
        )

    params.tweak_layers = bpy.props.BoolVectorProperty(
        size=32,
        description="Layers for the tweak controls to be on",
        default=tuple([i == 1 for i in range(0, 32)])
        )

    # IK controls
    params.generate_ik = bpy.props.BoolProperty(name="Generate IK controls", default=False)

    params.ik_parent_bone = bpy.props.StringProperty(
        name="IK parent bone", default="",
        description="Bone to use for 'IK follow parent' (defaults to the actual parent)"
        )

    # Setting up extra ik layers
    params.ik_extra_layers = bpy.props.BoolProperty(
        name="ik_extra_layers",
        default=False,
        description=""
        )

    params.ik_layers = bpy.props.BoolVectorProperty(
        size=32,
        description="Layers for the ik control to be on",
        default=tuple([i == 1 for i in range(0, 32)])
        )


def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.
    """
    r = layout.row()
    r.label(text="Bend rotation axis:")
    r.prop(params, "primary_rotation_axis", text="")

    layout_layer_selection_ui(layout, params, "tweak_extra_layers", "tweak_layers")

    layout.prop(params, "generate_ik")

    if params.generate_ik:
        layout.prop_search(params, "ik_parent_bone", bpy.context.object.pose, "bones")

        layout_layer_selection_ui(layout, params, "ik_extra_layers", "ik_layers")


def create_sample(obj):
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('palm.04.L')
    bone.head[:] = 0.0043, -0.0030, -0.0026
    bone.tail[:] = 0.0642, 0.0037, -0.0469
    bone.roll = -2.5155
    bone.use_connect = False
    bones['palm.04.L'] = bone.name
    bone = arm.edit_bones.new('f_pinky.01.L')
    bone.head[:] = 0.0642, 0.0037, -0.0469
    bone.tail[:] = 0.0703, 0.0039, -0.0741
    bone.roll = -1.9749
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['palm.04.L']]
    bones['f_pinky.01.L'] = bone.name
    bone = arm.edit_bones.new('f_pinky.02.L')
    bone.head[:] = 0.0703, 0.0039, -0.0741
    bone.tail[:] = 0.0732, 0.0044, -0.0965
    bone.roll = -1.9059
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['f_pinky.01.L']]
    bones['f_pinky.02.L'] = bone.name
    bone = arm.edit_bones.new('f_pinky.03.L')
    bone.head[:] = 0.0732, 0.0044, -0.0965
    bone.tail[:] = 0.0725, 0.0046, -0.1115
    bone.roll = -1.7639
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['f_pinky.02.L']]
    bones['f_pinky.03.L'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['palm.04.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    pbone = obj.pose.bones[bones['f_pinky.01.L']]
    pbone.rigify_type = 'limbs.super_finger'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.separate_extra_layers = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.extra_layers = [False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.tweak_extra_layers = False
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['f_pinky.02.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['f_pinky.03.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in arm.edit_bones:
        bone.select = False
        bone.select_head = False
        bone.select_tail = False
    for b in bones:
        bone = arm.edit_bones[bones[b]]
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        arm.edit_bones.active = bone





