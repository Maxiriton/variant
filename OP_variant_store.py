import uuid
from time import time
import bpy
from bpy.types import Operator, PropertyGroup, NodeTreeInterfaceSocketGeometry, NodeTreeInterfacePanel, NodeTreeInterfaceSocketMatrix
from bpy.props import BoolProperty, IntProperty, CollectionProperty, StringProperty
from .utils import get_addon_prefs

PROPS = 'props'
MATS = 'mats'
CAMERA = 'camera'
MODIFIERS = 'modifiers'
LIGHT = 'light'

SELECT_SET = 341
SCENE_DATA = 137

SELECTION = "selection"
SCENE = "scene"

PROPS_IGNORE_LIST = ['__doc__','__module__','__slots__','bl_rna','rna_type','execution_time','is_override_data','persistent_uid']
TYPES_IGNORE_LIST = [NodeTreeInterfaceSocketGeometry, NodeTreeInterfacePanel, NodeTreeInterfaceSocketMatrix]


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
            
def set_actual_property(base_data, str_prop, value,refresh_scene=False):
    subprops = str_prop.split('.')
    cur_data = base_data
    for index, cur_lvl_prop in enumerate(subprops):
        if index == len(subprops) -1:
            try:
                setattr(cur_data, cur_lvl_prop, value)
            except:
                print(f"Error while setting attribute {str_prop} - {value}")
        else:
            try:
                next_data = getattr(cur_data, cur_lvl_prop)
                cur_data = next_data
            except:
                return None
    if refresh_scene:
        bpy.context.view_layer.update()

def set_geo_nodes_input_property(modifier, identifier, value):
    modifier[identifier] = value 

def store_properties(context, obj, properties):
    result = {}
    for prop in properties:
        prop = prop.strip() #sanity check
        prop_value = get_actual_property(obj, prop)
        # print(f"{obj} - {prop} - {prop_value}")
        if prop_value is not None:
            result[prop] = prop_value
    return result


def apply_properties(context, datablock,stored_properties):   
    for key, value in stored_properties.items():
        set_actual_property(datablock, key, value)

def get_object_materials(context, obj):
    result = []
    for mat in obj.material_slots:
        result.append(mat.name)
    return result

def get_modifier_stack_params(context, obj):
    result = {}
    for modifier in obj.modifiers:
        props = {}
        if modifier.type == 'NODES':
            for input in modifier.node_group.interface.items_tree:
                if type(input) in TYPES_IGNORE_LIST:
                    continue
                value =  modifier[input.identifier]
                #Special case for object and Collection, we only store the name.
                # if type(value) in [bpy.types.Object, bpy.types.Collection]:
                #     value = value.name
                props[input.identifier] = value
        else:
            for attr in dir(modifier):
                if attr in PROPS_IGNORE_LIST:
                    continue
                prop = get_actual_property(modifier, attr)
                props[attr] = prop
        result[modifier.name] = props
        # print(result)
    return result

def set_modifier_stack_parameters(obj, param_dict):
    for mod_name, dict in param_dict.items():
        mod = obj.modifiers.get(mod_name)
        if not mod:
            continue
        if mod.type == 'NODES':
            for key, value in dict.items():
                set_geo_nodes_input_property(mod, key, value)
        else:
            for key, value in dict.items():
                set_actual_property(mod, key, value)

def set_object_materials(obj, stored_mats_list):
    for index, material_name in enumerate(stored_mats_list):
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
    ) # type: ignore

    def execute(self, context):
        start_time = time()
        objects = context.selected_objects if self.only_selected else context.scene.objects
        variant_UUID = str(uuid.uuid4())

        object_props_to_store = get_addon_prefs().object_properties_to_store.split(',')
        camera_props_to_store = get_addon_prefs().camera_properties_to_store.split(',')
        light_props_to_store = get_addon_prefs().light_properties_to_store.split(',')

        for obj in objects:
            all = {}
            all[PROPS] = store_properties(context, obj, object_props_to_store)
            if obj.type == 'CAMERA':
                all[CAMERA] = store_properties(context, obj.data, camera_props_to_store)
            elif obj.type == 'LIGHT':
                #TODO apply the light type first as it seems it doesn't apply to properties otherwise
                all[LIGHT] = store_properties(context, obj.data, light_props_to_store)
            if obj.type in ['MESH','CURVE','SURFACE','FONT','META']:
                all[MATS] = get_object_materials(context, obj)
                all[MODIFIERS] = get_modifier_stack_params(context, obj)
            obj[variant_UUID] =  all

        render_props_to_store = get_addon_prefs().render_properties_to_store.split(',')
        context.scene[variant_UUID] = store_properties(context, context.scene, render_props_to_store)

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

            for key in stored_properties.keys():
                if key == PROPS:
                    apply_properties(context, obj, stored_properties[PROPS])
                elif key == CAMERA:
                    apply_properties(context, obj.data, stored_properties[CAMERA])
                elif key == LIGHT:
                    apply_properties(context,obj.data, stored_properties[LIGHT])
                elif key == MODIFIERS:
                    set_modifier_stack_parameters(obj, stored_properties[MODIFIERS])
                elif key == MATS:
                    set_object_materials(obj, stored_properties[MATS])
                
        try: 
            stored_scene_properties  = context.scene[active_var.uuid]
            apply_properties(context, context.scene, stored_scene_properties )
        except:
            pass
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