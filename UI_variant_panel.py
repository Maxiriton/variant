import bpy
from bpy.types import Panel

class VariantPanel(Panel):
    """Variant UI in property Windows"""
    bl_idname="RENDER_PT_variant"
    bl_description = "Variant UI"
    bl_label = "Variant"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
            layout = self.layout

            row = layout.row()
            row.operator("va.store_scene_variant")


### Registration
classes = (
    VariantPanel,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)