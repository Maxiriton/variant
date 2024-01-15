# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Variant",
    "author": "Henri Hebeisen",
    "version": (0, 0, 1),
    "blender": (4, 0, 2),
    "location": "3D View > Properties Region > View",
    "description": "Variant Management",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
    }

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, EnumProperty

from . import OP_variant_store
from . import UI_variant_panel



class Variant_prefs(AddonPreferences):
    bl_idname = __package__

    ## tabs
    pref_tabs : EnumProperty(
        items=(('PREF', "Preferences", "Variant addon preferences"),
               ('KEYS', "Shortcuts", "Customize addon shortcuts")
               ),
               default='PREF')

    store_obj_location : BoolProperty(
        name="Store Objects Location",
        default=True
    )

    store_obj_visibility : BoolProperty(
        name="Store Objects Visibility",
        default=True
    )

    def draw(self, context):
        layout = self.layout

        row= layout.row(align=True)
        row.prop(self, "pref_tabs", expand=True)

        if self.pref_tabs == 'PREF':
            box = layout.box()
            box.label(text='Project settings')
            box.prop(self, "store_obj_location")
            box.prop(self, "store_obj_visibilty")
            
        if self.pref_tabs == 'KEYS':
            box = layout.box()
            box.label(text='Shortcuts added by 3.0 Tools with context scope:')


classes = (
    Variant_prefs,
)

addon_modules = (
    OP_variant_store,
    UI_variant_panel,

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for mod in addon_modules:
        mod.register()

def unregister():
    for mod in reversed(addon_modules):
        mod.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
