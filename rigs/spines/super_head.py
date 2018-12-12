#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>

import bpy

from itertools import count, repeat

from ..chain_rigs import TweakChainRig, SimpleChainRig

from ...utils.errors import MetarigError
from ...utils.layers import ControlLayersOption
from ...utils.naming import strip_org, make_deformer_name, make_mechanism_name
from ...utils.bones import BoneDict, put_bone, align_bone_to_axis, align_bone_orientation
from ...utils.bones import is_same_position, is_connected_position
from ...utils.widgets_basic import create_circle_widget, create_cube_widget
from ...utils.widgets_special import create_neck_bend_widget, create_neck_tweak_widget
from ...utils.misc import map_list, map_apply

from ...base_rig import *


class Rig(TweakChainRig):
    """
    Head rig with long neck support and connect option.
    """

    bbone_segments = 8

    def initialize(self):
        if len(self.bones.org) < 2:
            raise MetarigError("RIGIFY ERROR: Bone '%s': input to rig type must be a chain of 3 or more bones" % (strip_org(self.base_bone)))

        self.use_connect = self.params.connect_chain
        self.use_connect_master = False
        self.use_connect_tweak = False

        self.long_neck = len(self.bones.org) > 3
        self.length = sum([self.get_bone(b).length for b in self.bones.org])

        if self.use_connect:
            parent = self.rigify_parent

            if not isinstance(parent, SimpleChainRig):
                raise MetarigError("RIGIFY ERROR: Bone '%s': cannot connect to non-chain parent rig." % (strip_org(self.base_bone)))

            if not is_connected_position(self.obj, parent.bones.org[-1], self.bones.org[0]):
                raise MetarigError("RIGIFY ERROR: Bone '%s': cannot connect chain - bone position is disjoint." % (strip_org(self.base_bone)))


    def prepare_bones(self):
        orgs = self.bones.org

        if self.use_connect:
            # Exactly match bone position to parent
            self.get_bone(orgs[0]).head = self.get_bone(self.rigify_parent.bones.org[-1]).tail

    ####################################################
    # Main control bones

    @stage_generate_bones
    def make_control_chain(self):
        orgs = self.bones.org
        ctrl = self.bones.ctrl

        ctrl.neck = self.make_neck_control_bone(orgs[0], 'neck', orgs[-1])
        ctrl.head = self.make_head_control_bone(orgs[-1], 'head')
        if self.long_neck:
            ctrl.neck_bend = self.make_neck_bend_control_bone(orgs[0], 'neck_bend', ctrl.neck)

    def make_neck_control_bone(self, org, name, org_head):
        name = self.copy_bone(org, name, parent=False)

        # Neck spans all neck bones (except head)
        self.get_bone(name).tail = self.get_bone(org_head).head

        return name

    def make_neck_bend_control_bone(self, org, name, neck):
        name = self.copy_bone(org, name, parent=False)
        neck_bend_eb = self.get_bone(name)

        # Neck pivot position
        neck_bones = self.bones.org
        if (len(neck_bones)-1) % 2:     # odd num of neck bones (head excluded)
            center_bone = self.get_bone(neck_bones[int((len(neck_bones))/2) - 1])
            neck_bend_eb.head = (center_bone.head + center_bone.tail)/2
        else:
            center_bone = self.get_bone(neck_bones[int((len(neck_bones)-1)/2) - 1])
            neck_bend_eb.head = center_bone.tail

        align_bone_orientation(self.obj, name, neck)
        neck_bend_eb.length = self.get_bone(neck).length / 2

        return name

    def make_head_control_bone(self, org, name):
        return self.copy_bone(org, name, parent=False)

    @stage_parent_bones
    def parent_control_chain(self):
        bones = self.bones
        self.set_bone_parent(bones.ctrl.neck, bones.mch.rot_neck)
        self.set_bone_parent(bones.ctrl.head, bones.mch.rot_head)
        if self.long_neck:
            self.set_bone_parent(bones.ctrl.neck_bend, bones.mch.stretch)

    @stage_configure_bones
    def configure_control_chain(self):
        bones = self.bones
        self.configure_control_bone(bones.org[0], bones.ctrl.neck)
        self.configure_control_bone(bones.org[-1], bones.ctrl.head)
        if self.long_neck:
            self.configure_control_bone(bones.org[0], bones.ctrl.neck_bend)

    @stage_generate_widgets
    def make_control_widgets(self):
        ctrl = self.bones.ctrl
        self.make_neck_widget(ctrl.neck)
        self.make_head_widget(ctrl.head)
        if self.long_neck:
            self.make_neck_bend_widget(ctrl.neck_bend)

    def make_neck_widget(self, ctrl):
        radius = 1/max(1, len(self.bones.mch.chain))

        create_circle_widget(
            self.obj, ctrl,
            radius=radius,
            head_tail=0.5,
            bone_transform_name=None
        )

    def make_neck_bend_widget(self, ctrl):
        radius = 1/max(1, len(self.bones.mch.chain))

        create_neck_bend_widget(
            self.obj, ctrl,
            radius=radius/2,
            head_tail=0.0,
            bone_transform_name=None
        )

    def make_head_widget(self, ctrl):
        # place wgt @ middle of head bone for long necks
        if self.long_neck:
            head_tail = 0.5
        else:
            head_tail = 1.0

        create_circle_widget(
            self.obj, ctrl,
            radius              = 0.5,
            head_tail           = head_tail,
            with_line           = False,
            bone_transform_name = None
        )

    ####################################################
    # MCH bones associated with main controls

    @stage_generate_bones
    def make_mch_control_bones(self):
        orgs = self.bones.org
        mch = self.bones.mch

        mch.rot_neck = self.make_mch_rotation_bone(orgs[0], 'ROT-neck')
        mch.rot_head = self.make_mch_rotation_bone(orgs[-1], 'ROT-head')
        mch.stretch = self.make_mch_stretch_bone(orgs[0], 'STR-neck', orgs[-1])

    def make_mch_rotation_bone(self, org, name):
        name = self.copy_bone(org, make_mechanism_name(name), parent=True)
        self.get_bone(name).length = self.length / 5
        return name

    def make_mch_stretch_bone(self, org, name, org_head):
        name = self.copy_bone(org, make_mechanism_name(name), parent=False)
        self.get_bone(name).tail = self.get_bone(org_head).head
        return name

    @stage_parent_bones
    def align_mch_rotation_bones(self):
        # Choose which bone to follow
        mch = self.bones.mch
        parent = self.rigify_parent

        if self.use_connect and 'master' in parent.bones.ctrl:
            self.use_connect_master = True
            self.follow_bone = parent.bones.ctrl.master
        else:
            self.follow_bone = 'root'

        # Align rot bone orientations to it
        align_bone_orientation(self.obj, mch.rot_neck, self.follow_bone)
        align_bone_orientation(self.obj, mch.rot_head, self.follow_bone)

    @stage_parent_bones
    def parent_mch_control_bones(self):
        bones = self.bones
        self.set_bone_parent(bones.mch.rot_head, bones.ctrl.neck)
        self.set_bone_parent(bones.mch.stretch, bones.ctrl.neck)

    @stage_configure_bones
    def configure_follow_properties(self):
        # Choose where to put custom properties
        controls = self.bones.ctrl.flatten()

        if self.use_connect_master:
            self.prop_bone = self.follow_bone
            controls += self.rigify_parent.bones.ctrl.flatten()
        else:
            self.prop_bone = self.ctrl.head

        # Generate properties and script
        self.make_property(self.prop_bone, 'neck_follow', default=0.5)
        self.make_property(self.prop_bone, 'head_follow', default=0.0)

        self.script.add_panel_selected_check(controls)
        self.script.add_panel_custom_prop(self.prop_bone, 'neck_follow', slider=True)
        self.script.add_panel_custom_prop(self.prop_bone, 'head_follow', slider=True)

    @stage_rig_bones
    def rig_mch_control_bones(self):
        mch = self.bones.mch
        self.rig_mch_rotation_bone(mch.rot_neck, 'neck_follow')
        self.rig_mch_rotation_bone(mch.rot_head, 'head_follow')
        self.rig_mch_stretch_bone(mch.stretch, self.bones.ctrl.head)

    def rig_mch_rotation_bone(self, mch, prop_name):
        con = self.make_constraint(mch, 'COPY_ROTATION', self.follow_bone)
        self.make_constraint(mch, 'COPY_SCALE', self.follow_bone)

        self.make_driver(con, 'influence', variables=[(self.prop_bone, prop_name)], polynomial=[1,-1])

    def rig_mch_stretch_bone(self, mch, head):
        self.make_constraint(mch, 'DAMPED_TRACK', head)
        self.make_constraint(mch, 'STRETCH_TO', head)

    ####################################################
    # MCH IK chain for the long neck

    @stage_generate_bones
    def make_mch_ik_chain(self):
        orgs = self.bones.org
        if self.long_neck:
            self.bones.mch.ik = map_list(self.make_mch_ik_bone, orgs[0:-1])

    def make_mch_ik_bone(self, org):
        return self.copy_bone(org, make_mechanism_name('IK-'+strip_org(org)), parent=False)

    @stage_parent_bones
    def parent_mch_ik_chain(self):
        if self.long_neck:
            ik = self.bones.mch.ik
            self.set_bone_parent(ik[0], self.bones.ctrl.tweak[0])
            self.parent_bone_chain(ik, use_connect=True)

    @stage_rig_bones
    def rig_mch_ik_chain(self):
        if self.long_neck:
            ik = self.bones.mch.ik
            head = self.bones.ctrl.head
            map_apply(self.rig_mch_ik_bone, count(0), ik, repeat(len(ik)), repeat(head))

    def rig_mch_ik_bone(self, i, mch, ik_len, head):
        if i == ik_len - 1:
            self.make_constraint(mch, 'IK', head, chain_count=ik_len)

        self.get_bone(mch).ik_stretch = 0.1

    ####################################################
    # MCH chain for the middle of the neck

    @stage_generate_bones
    def make_mch_chain(self):
        orgs = self.bones.org
        self.bones.mch.chain = map_list(self.make_mch_bone, orgs[1:-1])

    def make_mch_bone(self, org):
        name = self.copy_bone(org, make_mechanism_name(strip_org(org)), parent=False)
        bone = self.get_bone(name)
        bone.length /= 4
        bone.use_inherit_scale = False
        return name

    @stage_parent_bones
    def align_mch_chain(self):
        for mch in self.bones.mch.chain:
            align_bone_orientation(self.obj, mch, self.bones.ctrl.neck)

    @stage_parent_bones
    def parent_mch_chain(self):
        mch = self.bones.mch
        map_apply(self.set_bone_parent, mch.chain, repeat(mch.stretch))

    @stage_rig_bones
    def rig_mch_chain(self):
        chain = self.bones.mch.chain
        if self.long_neck:
            ik = self.bones.mch.ik
            map_apply(self.rig_mch_bone_long, count(0), chain, repeat(len(chain)), ik[1:])
        else:
            map_apply(self.rig_mch_bone, count(0), chain, repeat(len(chain)))

    def rig_mch_bone_long(self, i, mch, len_mch, ik):
        ctrl = self.bones.ctrl

        self.make_constraint(mch, 'COPY_LOCATION', ik)

        step = 2/(len_mch+1)
        xval = (i+1)*step
        influence = 2*xval - xval**2    #parabolic influence of pivot

        self.make_constraint(
            mch, 'COPY_LOCATION', ctrl.neck_bend,
            influence=influence, use_offset=True, space='LOCAL'
        )

        self.make_constraint(mch, 'COPY_SCALE', ctrl.neck)

    def rig_mch_bone(self, i, mch, len_mch):
        ctrl = self.bones.ctrl

        nfactor = float((i + 1) / (len_mch + 1))
        self.make_constraint(
            mch, 'COPY_ROTATION', ctrl.head,
            influence=nfactor, space='LOCAL'
        )

    ####################################################
    # Tweak bones

    @stage_generate_bones
    def make_tweak_chain(self):
        orgs = self.bones.org
        self.bones.ctrl.tweak = map_list(self.make_tweak_bone, count(0), orgs[0:-1])

    def make_tweak_bone(self, i, org):
        if i == 0 and self.use_connect and isinstance(self.rigify_parent, TweakChainRig):
            # Share the last tweak bone of the parent rig
            parent_ctrl = self.rigify_parent.bones.ctrl
            name = parent_ctrl.tweak[-1]

            if not is_same_position(self.obj, name, org):
                raise MetarigError("RIGIFY ERROR: Bone '%s': cannot connect tweaks - position mismatch" % (strip_org(self.base_bone)))

            self.use_connect_tweak = True

            bone = self.get_bone(name)
            org_bone = self.get_bone(org)

            bone.head = org_bone.head
            bone.tail = org_bone.tail
            bone.roll = org_bone.roll
            bone.length /= 2

            name = self.rename_bone(name, 'tweak_' + strip_org(org))
            parent_ctrl.tweak[-1] = name
            return name

        else:
            return super(Rig,self).make_tweak_bone(i, org)

    @stage_parent_bones
    def parent_tweak_chain(self):
        ctrl = self.bones.ctrl
        mch = self.bones.mch

        if self.use_connect_tweak:
            # Steal the parent of the shared tweak bone before overriding it
            first_tweak_parent = self.get_bone_parent(ctrl.tweak[0])
            if first_tweak_parent:
                self.set_bone_parent(mch.rot_neck, first_tweak_parent)

        map_apply(self.set_bone_parent, ctrl.tweak, [ctrl.neck, *mch.chain])

    @stage_configure_bones
    def configure_tweak_chain(self):
        super(Rig,self).configure_tweak_chain()

        ControlLayersOption.TWEAK.assign(self.params, self.obj, self.bones.ctrl.tweak)

    @stage_rig_bones
    def generate_neck_tweak_widget(self):
        # Generate the widget early to override connected parent
        if self.long_neck:
            bone = self.bones.ctrl.tweak[0]
            create_neck_tweak_widget(self.obj, bone, size=1.0)

    ####################################################
    # ORG and DEF bones

    @stage_parent_bones
    def parent_deform_chain(self):
        super(Rig,self).parent_deform_chain()

        if self.use_connect:
            last_parent_deform = self.rigify_parent.bones.deform[-1]
            self.set_bone_parent(self.bones.deform[0], last_parent_deform, use_connect=True)

    @stage_configure_bones
    def configure_bbone_chain(self):
        self.get_bone(self.bones.deform[-1]).bone.bbone_segments = 1

    @stage_rig_bones
    def rig_org_chain(self):
        tweaks = self.bones.ctrl.tweak + [self.bones.ctrl.head]
        map_apply(self.rig_org_bone, self.bones.org, tweaks, tweaks[1:] + [None])


    ####################################################
    # SETTINGS

    @classmethod
    def add_parameters(self, params):
        """ Add the parameters of this rig type to the
            RigifyParameters PropertyGroup
        """

        params.connect_chain = bpy.props.BoolProperty(
            name='Connect chain',
            default=False,
            description='Connect the B-Bone chain to the parent rig'
        )

        # Setting up extra layers for the FK and tweak
        ControlLayersOption.TWEAK.add_parameters(params)

    @classmethod
    def parameters_ui(self, layout, params):
        """ Create the ui for the rig parameters."""

        r = layout.row()
        r.prop(params, "connect_chain")

        ControlLayersOption.TWEAK.parameters_ui(layout, params)


def create_sample(obj):
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('spine')
    bone.head[:] = 0.0000, 0.0552, 1.0099
    bone.tail[:] = 0.0000, 0.0172, 1.1573
    bone.roll = 0.0000
    bone.use_connect = False
    bones['spine'] = bone.name

    bone = arm.edit_bones.new('spine.001')
    bone.head[:] = 0.0000, 0.0172, 1.1573
    bone.tail[:] = 0.0000, 0.0004, 1.2929
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine']]
    bones['spine.001'] = bone.name

    bone = arm.edit_bones.new('spine.002')
    bone.head[:] = 0.0000, 0.0004, 1.2929
    bone.tail[:] = 0.0000, 0.0059, 1.4657
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.001']]
    bones['spine.002'] = bone.name

    bone = arm.edit_bones.new('spine.003')
    bone.head[:] = 0.0000, 0.0059, 1.4657
    bone.tail[:] = 0.0000, 0.0114, 1.6582
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.002']]
    bones['spine.003'] = bone.name

    bone = arm.edit_bones.new('spine.004')
    bone.head[:] = 0.0000, 0.0114, 1.6582
    bone.tail[:] = 0.0000, -0.013, 1.7197
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.003']]
    bones['spine.004'] = bone.name

    bone = arm.edit_bones.new('spine.005')
    bone.head[:] = 0.0000, -0.013, 1.7197
    bone.tail[:] = 0.0000, -0.0247, 1.7813
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.004']]
    bones['spine.005'] = bone.name

    bone = arm.edit_bones.new('spine.006')
    bone.head[:] = 0.0000, -0.0247, 1.7813
    bone.tail[:] = 0.0000, -0.0247, 1.9796
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.005']]
    bones['spine.006'] = bone.name


    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['spine']]
    pbone.rigify_type = 'spines.basic_spine'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'

    try:
        pbone.rigify_parameters.tweak_layers = [False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['spine.001']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['spine.002']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['spine.003']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['spine.004']]
    pbone.rigify_type = 'spines.super_head'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'

    try:
        pbone.rigify_parameters.connect_chain = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.tweak_layers = [False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['spine.005']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['spine.006']]
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
