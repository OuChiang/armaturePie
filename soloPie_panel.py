import bpy
from bpy.types import AddonPreferences,PropertyGroup,Menu,Operator,Panel
from bpy_extras.io_utils import ExportHelper,ImportHelper
import json

def get_armObject(context):
    soloPie = context.scene.solo_pie
    if soloPie.get('show_use_active',True):
        Obj = context.object
        if not Obj :
            return None
        if Obj.type != "ARMATURE":
            return None
        return Obj
    return soloPie.armature

# [ Pie Menu ]
class SOLOPIE_MT_pie_menu(Menu):
    bl_label = "Solo Pie"

    @classmethod
    def poll(cls, context):
        return get_armObject(context)
    
    def draw(self, context):
        
        def get_pie_titles(obj):
            pie_tree_wheel =[[] for i in range(0,8)]
            for bColl in obj.data.collections_all[:] :
                solo_lo = bColl.solo_pie
                if not solo_lo.is_title:
                    continue
                pie_wheel_int = int(solo_lo.pie_wheel_enum)
                pie_tree_wheel[pie_wheel_int].append(bColl)
            return pie_tree_wheel

        def lo_solo_btns(bColl,layout):
            btn_label = bColl.solo_pie.get('btn_label')
            Name = bColl.name if not btn_label else btn_label
            Icon = bColl.solo_pie.get('btn_icon','BLANK1')
            try:
                layout.operator('solo_pie.collection_solo', text=Name, icon=Icon).collection_name = Name
            except:
                layout.operator('solo_pie.collection_solo', text=Name, icon='CANCEL').collection_name = Name
        
        def lo_pie_row(pieWheel):
            row_dict = {}
            for bColl in pieWheel:
                rowNum = str(bColl.solo_pie.pie_row)
                if not row_dict.get(rowNum,None):
                    row_dict[rowNum] = []
                row_dict[rowNum].append(bColl)
            row_nums = list(row_dict.keys())
            row_nums.sort(key=lambda x:int(x))
            return [row_dict[num] for num in row_nums]

        def lo_pie_kids_space(boneColl,layout,btn_func):
            kids = boneColl.children
            if not kids: 
                return None
            row_out = layout.row(align=True)
            row_out.separator(factor=2, type='SPACE')
            col_in = row_out.column(align=True)
            for kid in kids:
                if kid.solo_pie.is_title:
                    continue
                btn_func(kid,col_in)
                lo_pie_kids_space(kid,col_in,btn_func)
        
        Obj = get_armObject(context)
        Titles = get_pie_titles(Obj)
        # [ Main Draw ]
        layout = self.layout
        # Center Functions
        col = layout.column()
        col.alignment = 'CENTER'
        box_label = col.box()
        #box_label.alert = True
        box_label.label(text= Obj.name)
        row = col.row(align=True)
        row.operator("solo_pie.collection_unsolo_all",text='',icon='SOLO_OFF')
        row.operator("solo_pie.pie_display_options",text='',icon='OVERLAY')
        
        # Pie Layout
        for pieWheel in Titles:
            lo_pie = layout.menu_pie()
            col_out =  lo_pie.column(align=False)
            if not pieWheel: 
                continue
            # - Row
            row = col_out.row()
            pieRows = lo_pie_row(pieWheel)
            for pieRow in pieRows:
                col = row.column(align=False)
                if not pieRow: 
                    continue
                # - Index
                pieRow.sort(key=lambda x:x.solo_pie.pie_index)
                for bColl in pieRow:
                    col_in = col.column(align=True)
                    lo_solo_btns(bColl,col_in)
                    lo_pie_kids_space(bColl,col_in,lo_solo_btns)

pie_wheel_directions = [ "Left","Right", "Down", "Up", "Left Up", "Right Up", "Left Down", "Right Down"]

# [ Sidebar Panel ]
# -- Preset Menu --
class SOLOPIE_MT_settings_preset(Menu):
    bl_label = "Solo Settings Preset"

    @classmethod
    def poll(cls, context):
        if not context.object :
            return False
        return context.object.type == 'ARMATURE'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("solo_pie.preset_save")
        layout.operator("solo_pie.preset_load")

# -- Setting Panel --
class SOLOPIE_PT_sidebar_main(Panel):
    bl_label = "Solo Pie"
    bl_idname = "SOLOPIE_PT_sidebar_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ArmPie"
    bl_options = {'DEFAULT_CLOSED','HEADER_LAYOUT_EXPAND'}
    bl_order = -1
    @classmethod
    def poll(cls, context):
        if not context.object :
            return False
        return context.object.type == 'ARMATURE'
    def draw_header_preset(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.menu(SOLOPIE_MT_settings_preset.__name__, text="",icon="DOWNARROW_HLT")
    def draw(self, context):
        Arm = context.object.data

        layout = self.layout
        layout.template_list(
            "SOLOPIE_UL_bone_collections","",Arm,"collections_all",Arm.collections,"active_index",rows = 8
            )

# -- Settings Sub Panel --
class SOLOPIE_PT_button_settings(Panel):
    bl_label = "Solo Settings"
    bl_idname = "SOLOPIE_PT_button_settings"
    bl_parent_id = 'SOLOPIE_PT_sidebar_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ArmPie"
    bl_options = {'DEFAULT_CLOSED','HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if not context.object :
            return False
        return context.object.type == 'ARMATURE'
    def draw(self, context):
        bColl = context.object.data.collections.active
        if not bColl:
            return None
        soloSettings = bColl.solo_pie
        if not soloSettings:
            return None
        layout = self.layout
        col = layout.column()
        split_factor = 0.3
        use_icon = bColl.solo_pie.get("btn_icon",'BLANK1')
        split_icon = col.split(factor=split_factor)
        split_icon.alignment='RIGHT'
        split_icon.label(text='Icon')
        try :
            split_icon.prop(bColl.solo_pie, "btn_icon",text='',placeholder='Icon',icon=use_icon)
        except:
            split_icon.alert =True
            split_icon.prop(bColl.solo_pie, "btn_icon",text='',placeholder='Icon',icon='CANCEL')
        
        split_name = col.split(factor=split_factor)
        split_name.alignment='RIGHT'
        split_name.label(text='Name')
        split_name.prop(bColl.solo_pie, "btn_label",text='',placeholder='Name')
        if soloSettings.get("is_title"):
            wheel_int = soloSettings.get('pie_wheel_enum',0)
            enumText = pie_wheel_directions[wheel_int]

            split_position = col.split(factor=split_factor)
            split_position.alignment='RIGHT'
            split_position.label(text='Position')
            col_pos_v = split_position.column(align=True)
            col_pos_v.prop_menu_enum(bColl.solo_pie, "pie_wheel_enum",text=enumText)
            col_pos_v.prop(bColl.solo_pie, "pie_row",text="row")
            col_pos_v.prop(bColl.solo_pie, "pie_index",text="index")

# -- Solo Collections UI List --
class SOLOPIE_UL_bone_collections(bpy.types.UIList):
    """UIList for Settings Armature Solo Pie Menu"""
    def parent_num(self,bColl,num):
        if not bColl.parent:
            return num
        return self.parent_num(bColl.parent,num+1)
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        
        soloPie = item.solo_pie
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            parentNum = self.parent_num(item,0)
            row = layout.row(align=True)
            row.label(text='',icon=soloPie.btn_icon)
            
            row.prop(soloPie, "is_title", text="")
            for i in range(parentNum):
                row.label(icon='BLANK1')

            row.prop(item,'name',text='',emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
    # Collections order & relationship
    def filter_items(self, context, data, propname):
        bcolls = getattr(data, propname)
        flt_flags = []
        flt_neworder = []
        neworder = []

        for bcoll in bcolls:
            if not bcoll.parent:
                neworder.append(bcoll.name)
            if bcoll.name not in neworder:
                pt_id = neworder.index(bcoll.parent.name)
                neworder.insert(pt_id+1,bcoll.name)

            bcoll_id = neworder.index(bcoll.name)
            children = bcoll.children[:]
            children.sort(key = lambda x : (x.child_number)*-1)
            for child in children :
                neworder.insert(bcoll_id+1,child.name)
        
        flt_neworder = [neworder.index(bcoll.name) for bcoll in bcolls]
        return flt_flags,flt_neworder

# --- Register ---
classes = [
    SOLOPIE_MT_settings_preset,
    SOLOPIE_UL_bone_collections,
    SOLOPIE_PT_sidebar_main,
    SOLOPIE_PT_button_settings,
    SOLOPIE_MT_pie_menu,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    classes.reverse
    for cls in classes:
        bpy.utils.unregister_class(cls)