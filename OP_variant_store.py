import uuid
from time import time
import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import BoolProperty, IntProperty, CollectionProperty, StringProperty
from .utils import get_addon_prefs

PROPS = 'props'
MATS = 'mats'
CAMERA = 'camera'

SELECT_SET = 341
SCENE_DATA = 137

SELECTION = "selection"
SCENE = "scene"

def get_actual_property(base_data, str_prop):
    ''' Utility to get the prop from a string property path
    this allow to store property from a given path like 'dof.use_dof' '''
    subprops = str_prop.split('.')
    cur_data = base_data
    for index, cur_lvl_prop in enumerate(subprops):
        if index == len(subprops) -1:
            try:
                value = getattr(cur_data, cur_lvl_prop)
                return value
            except:
                return None
        else:
            try:
                value = getattr(cur_data, cur_lvl_prop)
                cur_data = value
            except:
                return None
            
def set_actual_property(base_data, str_prop, value):
    subprops = str_prop.split('.')
    cur_data = base_data
    for index, cur_lvl_prop in enumerate(subprops):
        if index == len(subprops) -1:
            setattr(cur_data, cur_lvl_prop, value)
        else:
            try:
                next_data = getattr(cur_data, cur_lvl_prop)
                cur_data = next_data
            except:
                return None
            
            

def store_properties(context, obj, properties):
    result = {}
    for prop in properties:
        prop = prop.strip() #sanity check
        prop_value = get_actual_property(obj, prop)
        if prop_value is not None:
            result[prop] = prop_value
    return result


def apply_properties(context, obj,stored_properties, property_type, variant_uuid):
    if property_type not  in stored_properties:
        return None
    
    for key, value in stored_properties[property_type].items():
        set_actual_property(obj, key, value)

def get_object_materials(context, obj):
    result = []
    for mat in obj.material_slots:
        result.append(mat.name)
    return result

def set_object_materials(context, obj, variant_uuid):
    try:
        stored_properties = obj[variant_uuid]
    except :
        return None
    if MATS not in stored_properties:
        return None
    
    for index, material_name in enumerate(stored_properties[MATS]):
        obj.material_slots[index].material = bpy.data.materials[material_name]

class VariantItem(PropertyGroup):
    name: StringProperty(name="Variant Name", )
    uuid : StringProperty(name="Variant UUID")
    icon : IntProperty(name="Variant Icon")
    scope : StringProperty(name="Scope",default=SCENE)
    objects : StringProperty(name="Objects", description="Objects that are in this variant, if empty it means the whole scene", default="[]")


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
        start_time = time()
        objects = context.selected_objects if self.only_selected else context.scene.objects
        variant_UUID = str(uuid.uuid4())

        object_props_to_store = get_addon_prefs().object_properties_to_store.split(',')
        camera_props_to_store = get_addon_prefs().camera_properties_to_store.split(',')

        for obj in objects:
            all = {}
            all[PROPS] = store_properties(context, obj, object_props_to_store)
            all[MATS] = get_object_materials(context, obj)
            if obj.type == 'CAMERA':
                all[CAMERA] = store_properties(context, obj.data, camera_props_to_store)

            obj[variant_UUID] =  all

        new_var = context.scene.variants.add()
        new_var.name = f"Variant_{len(context.scene.variants)}"
        new_var.uuid = variant_UUID
        new_var.icon = SELECT_SET if self.only_selected else SCENE_DATA
        new_var.scope = SELECTION if self.only_selected else SCENE
        new_var.objects = str([obj.name for obj in objects])

        context.scene.active_variant = len(context.scene.variants) -1 
        self.report({"INFO"},f"New variant created in {time() - start_time:.3}s")
        return {"FINISHED"}

def get_objects_in_variant(string_list):
    names = string_list.strip("[]").split(', ')
    result = []
    for name in names:
        try:
            result.append(bpy.data.objects[name.strip("'")])
        except:
            continue
    return result

class VA_apply_scene_variant(Operator):
    bl_idname = "va.apply_scene_variant"
    bl_label = "Apply Scene Variant"
    bl_description = "Apply active variant"
    bl_options = {'REGISTER', 'UNDO'}

    prev_next : IntProperty(
        name="Previous, Current, Next",
        description="-1 for previous, 0 for current, 1 for next",
        default=0,
        min=-1,
        max=1
    )

    @classmethod
    def poll(cls, context):
        return  len(context.scene.variants) > 0

    def execute(self, context):
        if self.prev_next == -1 and context.scene.active_variant > 0:
            context.scene.active_variant -=1
        elif self.prev_next == 1 and context.scene.active_variant < len(context.scene.variants) -1: 
            context.scene.active_variant +=1

        active_var = context.scene.variants[context.scene.active_variant]

        for obj in get_objects_in_variant(active_var.objects):
            try:
                stored_properties = obj[active_var.uuid]
            except:
                continue
            apply_properties(context, obj, stored_properties, PROPS, active_var.uuid)
            set_object_materials(context, obj, active_var.uuid)
            if obj.type == 'CAMERA':
                apply_properties(context, obj.data,stored_properties, CAMERA, active_var.uuid)
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
        index_to_remove = context.scene.active_variant
        active_var = context.scene.variants[context.scene.active_variant]
        for obj in get_objects_in_variant(active_var.objects):
            try:
                del obj[active_var.uuid]
            except :
                continue

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