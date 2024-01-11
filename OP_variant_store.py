import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import BoolProperty, StringProperty, IntProperty, FloatVectorProperty


class VariantItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Reference Image Name", default="Unknown")
    blender_object_name : bpy.props.StringProperty(name="Blender object name", default="Unknown")
    is_movie : bpy.props.BoolProperty(name="Is movie", default=False)
    sound_channel : bpy.props.IntProperty(name="Sound Channel", min=0)
    sound_channel_name : bpy.props.StringProperty(name="Sound Channel Name")
    x_res : bpy.props.IntProperty(name="X Resolution in pixels")
    y_res : bpy.props.IntProperty(name="Y Resolution in pixels")
    opacity : bpy.props.FloatProperty(name="Global Opacity", default=1.0, min=0, max=1.0, update=OpacityUpdate)
    distance_to_camera : bpy.props.FloatProperty(name="Distance to camera",default=1.0,min=0.1, update=ChangeDistanceToCamera)
    color_overlay : bpy.props.FloatVectorProperty(name="Color Overlay", subtype='COLOR', default=(1, 1, 1, 1),
            size=4,
            min=0,
            max=1,
            update = ColorUpdate) 
    previous_distance_to_camera : bpy.props.FloatProperty(name="Previous Distance to camera")

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
        print('coucou')
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