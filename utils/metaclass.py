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

import collections


#=============================================
# Per-owner singleton class
#=============================================


class SingletonPluginMetaclass(type):
    """Metaclass for maintaining one instance per owner object per constructor arg set."""
    def __call__(cls, owner, *constructor_args):
        key = (cls, *constructor_args)
        try:
            return owner.plugin_map[key]
        except KeyError:
            new_obj = super(SingletonPluginMetaclass, cls).__call__(owner, *constructor_args)
            owner.plugin_map[key] = new_obj
            owner.plugin_list.append(new_obj)
            owner.plugin_list.sort(key=lambda obj: obj.priority, reverse=True)
            return new_obj

