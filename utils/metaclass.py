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

from types import FunctionType


#=============================================
# Class With Stages
#=============================================


def rigify_stage(stage):
    """Decorates the method with the specified stage."""
    def process(method):
        if not isinstance(method, FunctionType):
            raise ValueError("Stage decorator must be applied to a method definition")
        method._rigify_stage = stage
        return method
    return process


class StagedMetaclass(type):
    """
    Metaclass for rigs that manages assignment of methods to stages via @stage_* decorators.

    Using 'DEFINE_STAGES = True' inside the class definition will register all non-system
    method names from that definition as valid stages. After that, subclasses can
    register methods to those stages, to be called via rigify_invoke_stage.
    """
    def __new__(metacls, class_name, bases, namespace, **kwds):
        staged_bases = [base for base in bases if isinstance(base, StagedMetaclass)]

        # Compute the set of inherited stages
        stages = set().union(*[base._rigify_stages for base in staged_bases])

        # Add methods from current class if requested
        if 'DEFINE_STAGES' in namespace:
            del namespace['DEFINE_STAGES']

            for name, item in namespace.items():
                if name[0] != '_' and isinstance(item, FunctionType):
                    stages.add(name)

        # Create the class
        result = type.__new__(metacls, class_name, bases, dict(namespace))

        # Compute the inherited stage to method mapping
        stage_map = collections.defaultdict(collections.OrderedDict)
        method_map = {}

        for base in staged_bases:
            for stage_name, methods in base._rigify_stage_map.items():
                for method_name, method_class in methods.items():
                    if method_name in stages:
                        raise ValueError("Stage method '%s' inherited @stage_%s in class %s (%s)" %
                                         (method_name, stage_name, class_name, result.__module__))

                    # Check consistency of inherited stage assignment to methods
                    if method_name in method_map:
                        if method_map[method_name] != stage_name:
                            print("RIGIFY CLASS %s (%s): method '%s' has inherited both @stage_%s and @stage_%s\n" %
                                  (class_name, result.__module__, method_name, method_map[method_name], stage_name))
                    else:
                        method_map[method_name] = stage_name

                    stage_map[stage_name][method_name] = method_class

        # Scan newly defined methods for stage decorations
        for method_name, item in namespace.items():
            if isinstance(item, FunctionType):
                stage = getattr(item, '_rigify_stage', None)

                if stage and method_name in stages:
                    print("RIGIFY CLASS %s (%s): cannot use stage decorator on the stage method '%s' (@stage_%s ignored)" %
                            (class_name, result.__module__, method_name, stage))
                    continue

                # Ensure that decorators aren't lost when redefining methods
                if method_name in method_map:
                    if not stage:
                        stage = method_map[method_name]
                        print("RIGIFY CLASS %s (%s): missing stage decorator on method '%s' (should be @stage_%s)" %
                              (class_name, result.__module__, method_name, stage))
                    # Check that the method is assigned to only one stage
                    elif stage != method_map[method_name]:
                        print("RIGIFY CLASS %s (%s): method '%s' has decorator @stage_%s, but inherited base has @stage_%s" %
                              (class_name, result.__module__, method_name, stage, method_map[method_name]))

                # Assign the method to the stage, verifying that it's valid
                if stage:
                    if stage not in stages:
                        raise ValueError("Invalid stage name '%s' for method '%s' in class %s (%s)" %
                                         (stage, method_name, class_name, result.__module__))
                    else:
                        stage_map[stage][method_name] = result

        result._rigify_stages = frozenset(stages)
        result._rigify_stage_map = stage_map

        return result

    def make_stage_decorators(self):
        return [('stage_'+name, rigify_stage(name)) for name in self._rigify_stages]


class BaseStagedClass(object, metaclass=StagedMetaclass):
    def rigify_invoke_stage(self, stage):
        """Call all methods decorated with the given stage, followed by the callback."""
        cls = self.__class__
        assert(isinstance(cls, StagedMetaclass))
        assert(stage in cls._rigify_stages)

        for method_name in cls._rigify_stage_map[stage]:
            getattr(self, method_name)()

        getattr(self, stage)()


#=============================================
# Per-owner singleton class
#=============================================


class SingletonPluginMetaclass(StagedMetaclass):
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

