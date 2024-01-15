import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from .utils import get_addon_prefs

def get_object_properties(context, obj, variant_name):
    result = {}

    if get_addon_prefs().store_obj_location:
        result['location'] = obj.location
    if get_addon_prefs().store_obj_visibility:
        result['hide_viewport'] = obj.hide_viewport
        result['hide_render'] = obj.hide_render
    obj[variant_name] =  result

def set_object_properties(context, obj, variant_name):
    try: 
        properties = obj[variant_name]
        for key, value in properties.items():
            setattr(obj, key, value)
    except :
        print(f'Could not apply properties for {obj.name}')

class VA_store_scene_variant(Operator):
    bl_idname = "va.store_scene_variant"
    bl_label = "Store Current Scene State"
    bl_description = "Store Current Scene State."
    bl_options = {'REGISTER', 'UNDO'}

    only_selected : BoolProperty(
        name="Store Variant only for selected objects",
        default=False
    )

    def execute(self, context):
        objects = context.selected_objects if self.only_selected else bpy.context.scene.objects
        for obj in objects:
            get_object_properties(context, obj,'variant')
        return {"FINISHED"}

class VA_apply_scene_variant(Operator):
    bl_idname = "va.apply_scene_variant"
    bl_label = "Apply Scene Variant"
    bl_description = "Apply active variant"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.data.objects:
            set_object_properties(context, obj, 'variant')
        return {"FINISHED"}

### Registration
classes = (
    VA_store_scene_variant,
    VA_apply_scene_variant
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)