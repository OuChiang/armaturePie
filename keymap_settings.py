
import bpy
from bpy.types import Panel


# [ Keymap Register ]
addon_keymaps_list = []


def keymap_register():
    addon_keymaps = bpy.context.window_manager.keyconfigs.addon.keymaps
    addon_km = addon_keymaps.get('3D View',None)
    if not addon_km:
        addon_km = addon_keymaps.new(name='3D View', space_type='VIEW_3D')
    # Solo Pie
    keymap_0 = addon_km.keymap_items.new("solo_pie.call_solo_pie",
                                          type="RIGHTMOUSE",
                                          value="PRESS",
                                          ctrl=1,
                                          head=True)
    keymap_0.active=True
    addon_keymaps_list.append((addon_km,keymap_0))
    # Armature Picker
    keymap_1 = addon_km.keymap_items.new("armature_picker.dialog_panel",
                                          type="ONE",
                                          value="PRESS",
                                          shift=1,
                                          head=True)
    keymap_1.active=True
    addon_keymaps_list.append((addon_km,keymap_1))

def keymap_unregister():
    for km, kmi_idname in addon_keymaps_list:
        for kmi in km.keymap_items:
            if kmi.idname == kmi_idname.idname:
                km.keymap_items.remove(kmi)
    addon_keymaps_list.clear()



# [ Keymap Panel ]
class ARMPIE_PT_keymap(Panel):
    bl_label = "Keymaps"
    bl_idname = "ARMPIE_PT_keymap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ArmPie"
    bl_options = {'DEFAULT_CLOSED','HEADER_LAYOUT_EXPAND'}
    bl_order = -1
    def draw(self, context):
        # keymap
        wm = bpy.context.window_manager
            
        kc = wm.keyconfigs.user
        kms = kc.keymaps
        km = kms.get('Window')
        kis = km.keymap_items
        layout = self.layout
        col = layout.column(align=True)
        
        # [ Solo Pie Settings ]
        row_title = col.row()
        row_title.alignment = 'CENTER'
        row_title.label(text='Solo Pie')
        box_solo = col.box()
        row = box_solo.row()

        kmi_1 = addon_keymaps_list[0]
        row.label(text=kmi_1[1].idname)
        row.prop(kmi_1[1], "type", text="", full_event=True)

        # -- Use active or specific object --
        soloPie = context.scene.solo_pie
        showUseActive = soloPie.get('show_use_active',True)

        col_detail = box_solo.column(align=True)
        act_icon = 'RADIOBUT_ON' if showUseActive else 'RADIOBUT_OFF'
        act_text = "Using Active Object" if showUseActive else "Using Specific Object"
        col_detail.prop(soloPie,'show_use_active',text=act_text,icon=act_icon)

        if not showUseActive :
            row = col_detail.row()
            row.enabled = not showUseActive
            row.prop(soloPie,'armature',text='',icon='OUTLINER_OB_ARMATURE')
        
        col.separator(factor=4.0,type='LINE')

        # [ Armature Picker Settings ]
        row_title = col.row()
        row_title.alignment = 'CENTER'
        row_title.label(text='Armature Picker')
        box_solo = col.box()
        row = box_solo.row()

        kmi_2 = addon_keymaps_list[1]
        row.label(text=kmi_2[1].idname)
        row.prop(kmi_2[1], "type", text="", full_event=True)

        col.separator(factor=4.0)
# --- Register ---
def register():
    keymap_register()
    bpy.utils.register_class(ARMPIE_PT_keymap)

def unregister():
    bpy.utils.unregister_class(ARMPIE_PT_keymap)
    keymap_unregister()