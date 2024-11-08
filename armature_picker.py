import bpy
from bpy.types import Panel, Operator, Menu, PropertyGroup
from bl_operators.presets import AddPresetBase

link_type_items = ["ALL","Local","Overrided"]
link_type_icons = ["BLENDER","APPEND_BLEND","DECORATE_LIBRARY_OVERRIDE"]
filter_type_items = ["Include","Prefix","Suffix"]
class ARMPICKER_PR_props(PropertyGroup):
    is_hide_others :  bpy.props.BoolProperty(
        description='Hide other armature objects when you picked',
        default = False
        )

    link_type_items_enum =[(str(i),link_type_items[i],link_type_items[i],i ) for i in range(0,3)]
    link_type : bpy.props.EnumProperty(
        description='Sreach from local objects or overrideds',
        items = link_type_items_enum ,
        default = '0'
        )

    # Filter Settings
    use_filter : bpy.props.BoolProperty(
        description='Actived filter',
        default = False
        )
    filter_type_items_enum =[(str(i),filter_type_items[i],filter_type_items[i],i ) for i in range(0,3)]
    find_type : bpy.props.EnumProperty(
        description='Sreach with Include / Prefix / suffix',
        items = filter_type_items_enum 
        ,default = '0'
        )
    find_str : bpy.props.StringProperty(
        description='Sreach strings'
        )
    find_no_matter_case : bpy.props.BoolProperty(
        description='No matter lower or upper case',
        default = True
        )
    find_use_root_name: bpy.props.BoolProperty(
        description='Use overrided collection name',
        default = True
        )

    

# Select Arm & in to pose
class ARMPICKER_OT_armature_select(Operator):
    """Quick select armature object and in to mode"""
    bl_idname = "armature_picker.armature_select"
    bl_label = "Armature Object Select"

    select_object : bpy.props.StringProperty()
    is_in_pose_mode : bpy.props.BoolProperty()
    is_hide_others : bpy.props.BoolProperty()
    def execute(self, context):
        ViewLayer = context.view_layer
        # Get Select Object
        selObj = bpy.data.objects.get(self.select_object)
        if not selObj :
            return {'FINISHED'}

        # Back To Object Mode
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        
        # Show All Armature
        Objs = [[Obj,Obj.hide_viewport] for Obj in bpy.data.objects if Obj.type=='ARMATURE']
        for Obj in Objs:
            Obj[0].hide_viewport = False
            ViewLayer.objects[Obj[0].name].hide_set(False)

        if self.is_hide_others:
            # Reset hide_viewport
            for Obj in Objs:
                Obj[0].hide_viewport = True
                ViewLayer.objects[Obj[0].name].hide_set(True)

        #
        selObj.hide_viewport = False
        ViewLayer.objects[selObj.name].hide_set(False)
        bpy.ops.object.select_all(action='DESELECT')
        selObj.select_set(state=True)

        bpy.context.view_layer.objects.active = selObj

        if self.is_in_pose_mode :
            bpy.ops.object.posemode_toggle()
        return {'FINISHED'}

#  --- Preset ---
class ARMPICKER_MT_preset_panel(Menu):
    bl_label = "Armature picker preset settings"
    preset_subdir = "scene/armature_picker"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset

class ARMPICKER_OT_preset_panel(AddPresetBase, Operator):
    """Preset add & remove"""
    bl_idname = "armature_picker.filter_preset_add"
    bl_label = "Preset add & remove"
    preset_menu = "ARMPICKER_MT_preset_panel"
    preset_defines = ["arm = bpy.context.scene.armature_picker"]
    preset_values = [f"arm.{e}" for e in ["is_hide_others","link_type","use_filter","find_type","find_str","find_use_root_name"]]
    preset_subdir = "scene/armature_picker"


#---Settings
class ARMPICKER_OT_filter_settings(Operator):
    """Settings for armature picker filter"""
    bl_idname = "armature_picker.filter_settings"
    bl_label = "Armature picker filter"
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)
    
    def draw(self, context):
        arm_prop = context.scene.armature_picker
        link_type_int = arm_prop.get('link_type',0)

        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.menu(ARMPICKER_MT_preset_panel.__name__,text =ARMPICKER_MT_preset_panel.bl_label)
        row.operator(ARMPICKER_OT_preset_panel.bl_idname, text="", icon='ZOOM_IN')
        row.operator(ARMPICKER_OT_preset_panel.bl_idname, text="", icon='ZOOM_OUT').remove_active = True
        
        # Filter Bar
        row = col.row()
        row.prop(arm_prop,'use_filter',text='',icon="FILTER")
        box = col.box()
        box.enabled =  arm_prop.use_filter
        box_row = box.row(align=True)
        box_row.prop(arm_prop,'find_str',text='')
        box_row.prop(arm_prop,'find_type',text='')

        box.prop(arm_prop,'find_no_matter_case',text="No Matter Letter Case")

        # Use Root Name
        # Override Only
        if link_type_int == 2:
            box.prop(arm_prop,'find_use_root_name',text='Sreach Collecion Name')


#---Operator for Keymap
class ARMPICKER_OT_dialog_panel(Operator):
    """Armature picker dialog"""
    bl_idname = "armature_picker.dialog_panel"
    bl_label = "Armature Picker"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.alignment="CENTER"
        presetPanel = ARMPICKER_MT_preset_panel
        row.menu(presetPanel.__name__, text="",icon="PRESET")
        
        ARMPICKER_PT_armature_picker.draw(self, context)


class ARMPICKER_PT_armature_picker(Panel):
    """Creates a panel in the scene context of the properties editor"""
    bl_label = "Armature Picker"
    bl_idname = "ARMPICKER_PT_armature_picker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ArmPie"
    
    def draw_header_preset(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.menu(ARMPICKER_MT_preset_panel.__name__, text="",icon="PRESET")
    def draw(self, context):        
        scene = context.scene
        arm_prop = scene.armature_picker
        filter_use =  arm_prop.get('use_filter',False)
        link_type_int = arm_prop.get('link_type',0)
        sreach_type_int = arm_prop.get('find_type',0)
        sreach_string =  arm_prop.get('find_str','')
        sreach_useRoot =  arm_prop.get('find_use_root_name',False)
        is_skip_case =  arm_prop.get('find_no_matter_case',True)
        
        def get_arm_list():
            ArmObjs_all = [Obj for Obj in scene.objects if Obj.type=='ARMATURE']
            match link_type_int:
                case 0:
                    return ArmObjs_all
                case 1:
                    return [Obj for Obj in ArmObjs_all if not Obj.override_library]
                case 2:
                    return [Obj for Obj in ArmObjs_all if Obj.override_library]
                case _:
                    return None
            
        def name_check(Obj):
            if not filter_use:
                return True
            # If is Override Type And Use Root
            if link_type_int==2 and sreach_useRoot:
                Obj = Obj.override_library.hierarchy_root
            
            if not Obj:
                return False
            
            objName = Obj.name
            findStr = sreach_string
            if is_skip_case:
                objName = objName.upper()
                findStr = findStr.upper()
            match sreach_type_int:
                case 0: # Include
                    return  findStr in objName
                case 1: # Prefix
                    return objName.startswith(findStr)
                case 2: # Suffix
                    return objName.endswith(findStr)
                
                case _:
                    return False

        def LO_btn_row(Layout,Obj,is_hide_others,is_selected):
            row = Layout.row(align=True)
            selectedIcon = 'RESTRICT_SELECT_OFF' if is_selected else 'NONE'
            ObjName = Obj.name

            pie_selIcon = row.menu_pie()
            pie_selIcon.alignment='RIGHT'
            btn_sel = pie_selIcon.label(text='',icon=selectedIcon)

            pie_selBtn =  row.menu_pie()
            btn_sel = pie_selBtn.operator("armature_picker.armature_select",
                                      text=ObjName,
                                      emboss=False)
            btn_sel.select_object=ObjName
            btn_sel.is_in_pose_mode=False
            btn_sel.is_hide_others = is_hide_others

            btn_sel = row.operator("armature_picker.armature_select",text='',icon='POSE_HLT')
            btn_sel.select_object=ObjName
            btn_sel.is_in_pose_mode=True
            btn_sel.is_hide_others = is_hide_others

        
        ArmObjs = get_arm_list()

        layout = self.layout
        col = layout.column(align=True)
        # ---Func Bar---
        row = col.row(align=True)
        row.prop(arm_prop,'is_hide_others',text='',icon='POINTCLOUD_POINT')
        link_type_labelText = link_type_items[link_type_int]
        link_type_labelIcon = link_type_icons[link_type_int]
        row.prop_menu_enum(arm_prop,'link_type',text=link_type_labelText,icon=link_type_labelIcon)
        row.operator("armature_picker.filter_settings",text='',icon='FILTER')
        # --- 
        box = col.box()
        

        is_nothing_show = True
        for ArmObj in ArmObjs:
            if not name_check(ArmObj):
                continue
            LO_btn_row(box,ArmObj,arm_prop.is_hide_others,ArmObj.select_get())
            is_nothing_show = False
        

        if is_nothing_show : # if no found
            row = box.row(align=True)
            row.alert =True
            row.label(text = "No Found",icon='QUESTION')
            return None

classes = [ARMPICKER_OT_armature_select,
           ARMPICKER_OT_filter_settings,
           ARMPICKER_MT_preset_panel,
           ARMPICKER_OT_preset_panel,
           ARMPICKER_OT_dialog_panel,
           ARMPICKER_PT_armature_picker]

def register():
    bpy.utils.register_class(ARMPICKER_PR_props)
    bpy.types.Scene.armature_picker = bpy.props.PointerProperty(type= ARMPICKER_PR_props)
    
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    classes.reverse()
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.armature_picker
    bpy.utils.unregister_class(ARMPICKER_PR_props)
