import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from .utils import get_addon_prefs

def get_object_properties(context, obj):
    result = {}

    if get_addon_prefs().store_obj_location:
        result['matrix_local'] = obj.matrix_local
    if get_addon_prefs().store_obj_visibility:
        result['hide_viewport'] = obj.hide_viewport
        result['hide_render'] = obj.hide_render
    return result

class VA_store_scene_variant(Operator):
    bl_idname = "va.store_scene_variant"
    bl_label = "Store Current Scene State "
    bl_description = "Store Current Scene State."
    bl_options = {'REGISTER', 'UNDO'}

    only_selected : BoolProperty(
        name="Store Variant only for selected objects",
        default=False
    )

    def execute(self, context):
        objects = context.selected_objects if self.only_selected else bpy.data.objects
        for obj in objects:
            properties_to_store = get_object_properties(context, obj)
            obj['variant'] = properties_to_store
        return {"FINISHED"}

### Registration
classes = (
    VA_store_scene_variant,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)