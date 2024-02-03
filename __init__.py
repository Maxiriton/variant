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
    "blender": (4, 0, 1),
    "location": "3D View > Properties Region > View",
    "description": "Variant Management",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
    }

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, EnumProperty, StringProperty

from . import OP_variant_store
from . import UI_variant_panel


def update_func(self, context):
    """Clean and normalize properties to store in variant"""
    self.object_properties_to_store.strip()

class Variant_prefs(AddonPreferences):
    bl_idname = __package__

    ## tabs
    pref_tabs : EnumProperty(
        items=(('PREF', "Preferences", "Variant addon preferences"),
               ('KEYS', "Shortcuts", "Customize addon shortcuts")
               ),
               default='PREF')

    object_properties_to_store : StringProperty(
        name = "Object Properties to store", 
        default= 'location,rotation_euler,scale,hide_viewport,hide_render',
        update=update_func
    )

    camera_properties_to_store : StringProperty(
        name = "Camera Properties to store",
        default="type,ortho_scale,lens,lens_unit,shift_x,shift_y,clip_start,clip_end,sensor_fit,sensor_width,sensor_height,dof.use_dof"
    )

    render_properties_to_store : StringProperty(
        name = "Render Properties to store", 
        default="resolution_x,resolution_y"
    )

    def draw(self, context):
        layout = self.layout

        row= layout.row(align=True)
        row.prop(self, "pref_tabs", expand=True)

        if self.pref_tabs == 'PREF':
            box = layout.box()
            box.label(text='Project settings')
            box.prop(self, "object_properties_to_store")
            box.prop(self, "camera_properties_to_store")
            
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
