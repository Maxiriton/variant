import uuid
import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import BoolProperty, IntProperty, CollectionProperty, StringProperty
from .utils import get_addon_prefs

def get_object_properties(context, obj, variant_uuid):
    result = {}
    properties = get_addon_prefs().object_properties_to_store.split(',')
    for prop in properties:
        prop = prop.strip()
        try : 
            result[prop] = getattr(obj, prop)
        except: 
            print(f'No {prop} property for {obj.name}')
    obj[variant_uuid] =  result

def set_object_properties(context, obj, variant_uuid):
    try: 
        properties = obj[variant_uuid]
        for key, value in properties.items():
            setattr(obj, key, value)
    except :
        print(f'Could not apply properties for {obj.name}')

class VariantItem(PropertyGroup):
    name: StringProperty(name="Variant Name", )
    uuid : StringProperty(name="Variant UUID")

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
        objects = context.selected_objects if self.only_selected else bpy.data.objects
        variant_UUID = str(uuid.uuid4())

        for obj in objects:
            get_object_properties(context, obj,variant_UUID)

        new_var = context.scene.variants.add()
        new_var.name = f"Variant_{len(context.scene.variants)}"
        new_var.uuid = variant_UUID
        return {"FINISHED"}

class VA_apply_scene_variant(Operator):
    bl_idname = "va.apply_scene_variant"
    bl_label = "Apply Scene Variant"
    bl_description = "Apply active variant"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return  len(context.scene.variants) > 0

    def execute(self, context):
        active_var = context.scene.variants[context.scene.active_variant]
        for obj in bpy.data.objects:
            set_object_properties(context, obj, active_var.uuid)
        return {"FINISHED"}

### Registration
classes = (
    VA_store_scene_variant,
    VA_apply_scene_variant,
    VariantItem
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

    bpy.types.Scene.variants = CollectionProperty(type=VariantItem)
    bpy.types.Scene.active_variant = IntProperty(default=0)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)

    del bpy.types.Scene.active_variant
    del bpy.types.Scene.variants