import uuid
import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import BoolProperty, IntProperty, CollectionProperty, StringProperty
from .utils import get_addon_prefs

PROPS = 'props'
MATS = 'mats'
CAMERA = 'camera'

def get_object_properties(context, obj):
    result = {}
    properties = get_addon_prefs().object_properties_to_store.split(',')
    for prop in properties:
        prop = prop.strip()
        try :
            result[prop] = getattr(obj, prop)
        except:
            print(f'No {prop} property for {obj.name}')
    return result

def get_camera_properties(context, cam_data):
    result = {}
    properties = get_addon_prefs().camera_properties_to_store.split(',')
    for prop in properties:
        prop = prop.strip()
        try :
            result[prop] = getattr(cam_data, prop)
        except:
            print(f'No {prop} camera property for {cam_data.name}')
    return result

def get_object_materials(context, obj):
    result = []
    for mat in obj.material_slots:
        result.append(mat.name)
    return result

def set_object_properties(context, obj, variant_uuid):
    try:
        stored_properties = obj[variant_uuid]
        if PROPS in stored_properties:
            for key, value in stored_properties[PROPS].items():
                setattr(obj, key, value)
    except :
        print(f'Could not apply properties for {obj.name}')


def set_object_materials(context, obj, variant_uuid):
    try:
        stored_properties = obj[variant_uuid]
    except :
        print(f'Could not apply materials for {obj.name}')
        return None
    if MATS not in stored_properties:
        return None
    
    for index, material_name in enumerate(stored_properties[MATS]):
        obj.material_slots[index].material = bpy.data.materials[material_name]

def set_camera_properties(context, cam_obj, variant_uuid):
    try:
        stored_properties = cam_obj[variant_uuid]
    except :
        print(f'Could not retrieve camera properties for {cam_obj.name}')
        return None
    if CAMERA not in stored_properties:
        return None
    
    for key, value in stored_properties[CAMERA].items():
        setattr(cam_obj.data, key, value)

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
        objects = context.selected_objects if self.only_selected else context.scene.objects
        variant_UUID = str(uuid.uuid4())

        for obj in objects:
            all = {}
            all[PROPS] = get_object_properties(context, obj)
            all[MATS] = get_object_materials(context, obj)
            if obj.type == 'CAMERA':
                all[CAMERA] = get_camera_properties(context, obj.data)

            obj[variant_UUID] =  all

        new_var = context.scene.variants.add()
        new_var.name = f"Variant_{len(context.scene.variants)}"
        new_var.uuid = variant_UUID

        context.scene.active_variant = len(context.scene.variants) -1 
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
            set_object_materials(context, obj, active_var.uuid)
            if obj.type == 'CAMERA':
                set_camera_properties(context, obj, active_var.uuid)
        return {"FINISHED"}
    
class VA_remove_variant(Operator):
    """Remove a variant from the scene"""
    bl_idname = "va.remove_variant"
    bl_label = "Remove Variant"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.variants) > 0

    def execute(self, context):
        print('on est la ')
        index_to_remove = context.scene.active_variant
        active_var = context.scene.variants[context.scene.active_variant]
        for obj in bpy.data.objects:
            try:
                del obj[active_var.uuid]
            except :
                print(f'Could not delete variant  for {obj.name}')

        context.scene.variants.remove(index_to_remove)
        if index_to_remove == len(context.scene.variants):
            context.scene.active_variant = index_to_remove -1 
        else:
            context.scene.active_variant = index_to_remove

        return {'FINISHED'}

### Registration
classes = (
    VA_store_scene_variant,
    VA_apply_scene_variant,
    VA_remove_variant,
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