import bpy
from bpy.types import Panel, UIList


class VA_UL_variantList(UIList):
    """List of variant stored in scene """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        custom_icon = item.icon
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            layout.prop(item, "name", text="", emboss=False, icon_value=custom_icon)

        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class VariantPanel(Panel):
    """Variant UI in property Windows"""
    bl_idname="RENDER_PT_variant"
    bl_description = "Variant UI"
    bl_label = "Variant"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row()
        row.operator("va.store_scene_variant")
        row = layout.row()
        row.template_list("VA_UL_variantList", "", scene, "variants", scene, "active_variant")

        col = layout.column(align=True)
        row = col.row(align=True)
    
        button  = row.operator("va.apply_scene_variant", text="Previous Variant",icon='PREV_KEYFRAME')
        button.prev_next = -1
        row.operator("va.apply_scene_variant")
        button = row.operator("va.apply_scene_variant", text="Next Variant",icon='NEXT_KEYFRAME')
        button.prev_next = 1


### Registration
classes = (
    VariantPanel,
    VA_UL_variantList,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)