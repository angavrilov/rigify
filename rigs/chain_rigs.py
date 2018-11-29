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

from ..base_rig import *

from ..utils.errors import MetarigError
from ..utils.rig import connected_children_names
from ..utils.naming import strip_org, make_deformer_name
from ..utils.bones import put_bone
from ..utils.widgets_basic import create_bone_widget, create_sphere_widget
from ..utils.misc import map_list, map_apply


class SimpleChainRig(BaseRig):
    """A rig that consists of 3 connected chains of control, org and deform bones."""
    def find_org_bones(self, bone):
        return [bone.name] + connected_children_names(self.obj, bone.name)

    def initialize(self):
        if len(self.bones.org) <= 1:
            raise MetarigError("RIGIFY ERROR: Bone '%s': input to rig type must be a chain of 2 or more bones" % (strip_org(self.base_bone)))

    bbone_segments = None

    # Generate
    @stage_generate_bones
    def make_control_chain(self):
        self.bones.ctrl.main = map_list(self.make_control_bone, self.bones.org)

    def make_control_bone(self, org):
        return self.copy_bone(org, strip_org(org), parent=True)

    @stage_generate_bones
    def make_deform_chain(self):
        self.bones.deform = map_list(self.make_deform_bone, self.bones.org)

    def make_deform_bone(self, org):
        name = self.copy_bone(org, make_deformer_name(strip_org(org)), parent=True, bbone=True)
        if self.bbone_segments:
            self.get_bone(name).bbone_segments = self.bbone_segments
        return name

    # Parent
    @stage_parent_bones
    def parent_control_chain(self):
        self.parent_bone_chain(self.bones.ctrl.main, use_connect=True)

    @stage_parent_bones
    def parent_deform_chain(self):
        self.parent_bone_chain(self.bones.deform, use_connect=True)

    # Configure
    @stage_configure_bones
    def configure_control_chain(self):
        map_apply(self.configure_control_bone, self.bones.org, self.bones.ctrl.main)

    def configure_control_bone(self, org, ctrl):
        self.copy_bone_properties(org, ctrl)

    # Rig
    @stage_rig_bones
    def rig_org_chain(self):
        map_apply(self.rig_org_bone, self.bones.org, self.bones.ctrl.main)

    def rig_org_bone(self, org, ctrl):
        self.make_constraint(org, 'COPY_TRANSFORMS', ctrl)

    @stage_rig_bones
    def rig_deform_chain(self):
        map_apply(self.rig_deform_bone, self.bones.org, self.bones.deform)

    def rig_deform_bone(self, org, deform):
        self.make_constraint(deform, 'COPY_TRANSFORMS', org)

    # Widgets
    @stage_generate_widgets
    def make_control_widgets(self):
        map_apply(self.make_control_widget, self.bones.ctrl.main)

    def make_control_widget(self, ctrl):
        create_bone_widget(self.obj, ctrl)


class TweakChainRig(SimpleChainRig):
    """A rig that adds tweak controls to the triple chain."""

    # Generate
    @stage_generate_bones
    def make_tweak_chain(self):
        orgs = self.bones.org
        self.bones.ctrl.tweak = map_list(self.make_tweak_bone, count(0), orgs + orgs[-1:])

    def make_tweak_bone(self, i, org):
        name = self.copy_bone(org, 'tweak_' + strip_org(org), parent=False)

        self.get_bone(name).length /= 2

        if i == len(self.bones.org):
            put_bone(self.obj, name, self.get_bone(org).tail)

        return name

    # Parent
    @stage_parent_bones
    def parent_tweak_chain(self):
        ctrl = self.bones.ctrl
        map_apply(self.set_bone_parent, ctrl.tweak, ctrl.main + ctrl.main[-1:])

    # Configure
    @stage_configure_bones
    def configure_tweak_chain(self):
        map_apply(self.configure_tweak_bone, count(0), self.bones.ctrl.tweak)

    def configure_tweak_bone(self, i, tweak):
        tweak_pb = self.get_bone(tweak)

        if i == len(self.bones.org):
            tweak_pb.lock_rotation_w = True
            tweak_pb.lock_rotation = (True, True, True)
            tweak_pb.lock_scale = (True, True, True)
        else:
            tweak_pb.lock_rotation_w = False
            tweak_pb.lock_rotation = (True, False, True)
            tweak_pb.lock_scale = (False, True, False)

    # Rig
    @stage_rig_bones
    def rig_org_chain(self):
        tweaks = self.bones.ctrl.tweak
        map_apply(self.rig_org_bone, self.bones.org, tweaks, tweaks[1:])

    def rig_org_bone(self, org, tweak, next_tweak):
        self.make_constraint(org, 'COPY_TRANSFORMS', tweak)
        self.make_constraint(org, 'DAMPED_TRACK', next_tweak)
        self.make_constraint(org, 'STRETCH_TO', next_tweak)

    # Widgets
    @stage_generate_widgets
    def make_tweak_widgets(self):
        map_apply(self.make_tweak_widget, self.bones.ctrl.tweak)

    def make_tweak_widget(self, tweak):
        create_sphere_widget(self.obj, tweak)

