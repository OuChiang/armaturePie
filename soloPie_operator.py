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

#--- Solo Pie ---
class SOLOPIE_OT_collection_solo(Operator):
    """Solo bone collection"""
    bl_idname = "solo_pie.collection_solo"
    bl_label = "solo bone collection"
    
    collection_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return get_armObject(context)

    def execute(self, context):
        Obj = get_armObject(context)
        bColls = Obj.data.collections_all
        for bColl in bColls:
            bColl.is_solo = False
        
        bColl = bColls.get(self.collection_name)
        if not bColl:
            return {'FINISHED'}
        
        bColl.is_solo = True
        for kid in bColl.children[:]:
            kid.is_solo = True
            
        return {'FINISHED'}

class SOLOPIE_OT_collection_unsolo_all(Operator):
    """Un-solo all bone collections"""
    bl_idname = "solo_pie.collection_unsolo_all"
    bl_label = "Un-solo All"

    @classmethod
    def poll(cls, context):
        return get_armObject(context)
    
    def execute(self, context):
        Obj = get_armObject(context)
        bColls =  Obj.data.collections_all 
        for bColl in bColls:
            bColl.is_solo = False
        
        return {'FINISHED'}
    
class SOLOPIE_OT_display_options(Operator):
    """Armature display options"""
    bl_idname = "solo_pie.pie_display_options"
    bl_label = "Collection Display Options"

    @classmethod
    def poll(cls, context):
        return get_armObject(context)
        #return bpy.context.mode in ['EDIT_ARMATURE','POSE']
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)
    
    def draw(self, context):
        Obj = get_armObject(context)
        layout = self.layout
        col = layout.column()
        col.prop(Obj.data,'display_type',text='')
        col.prop(Obj,'show_in_front',icon='AXIS_FRONT')
        col.prop(Obj.data,'use_mirror_x',icon='MOD_MIRROR')
        row_relation = col.row()
        row_relation.prop(Obj.data, "relation_line_position", text="Relations", expand=True)
        



class SOLOPIE_OT_collection_show_title_only(Operator):
    """Show all titles and hide others"""
    bl_idname = "solo_pie.collection_show_title_only"
    bl_label = "Show Title Only"

    @classmethod
    def poll(cls, context):
        Obj = context.object
        if not Obj:
            return False
        return Obj.type=='ARMATURE'
    
    def execute(self, context):
        def show_kids(bColl):
            kids = bColl.children
            if not kids: return None
            for kid in kids:
                kid.is_visible = True
                show_kids(kid)

        collAll = context.object.data.collections_all
        
        # Hide All
        for bColl in collAll:
            bColl.is_visible = False
        
        bColls = [bColl for bColl in collAll if bColl.solo_pie.is_title]
        for bColl in bColls:
            bColl.is_visible = True
            show_kids(bColl)
        return {'FINISHED'}

class ARMATURE_OT_collection_hide_all(Operator):
    """Hide all bone collections"""
    bl_idname = "armature.collection_hide_all"
    bl_label = "Hide All"
    @classmethod
    def poll(cls, context):
        Obj = context.object
        if not Obj:
            return False
        return Obj.type=='ARMATURE'
    def execute(self, context):
        collAll = context.object.data.collections_all
        for bColl in collAll:
            bColl.is_visible = False
        return {'FINISHED'}


def solo_preset_draw_header(self, context):
    layout = self.layout
    pie = layout.menu_pie()
    pie.alignment = 'RIGHT'
    #row = pie.row(align=True)
    pie.operator("armature.pie_preset_save",text="Save")
    pie.operator("armature.pie_preset_load",text="Load")

# [ Solo Preset ]
class SOLOPIE_OT_preset_save(Operator, ExportHelper):
    """Save preset solo settings"""
    bl_idname = "solo_pie.preset_save"
    bl_label = "Save Settings"

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json",options={'HIDDEN'},maxlen=255)
    
    @classmethod
    def poll(cls, context):
        Obj = context.object
        if not Obj:
            return False
        return Obj.type=='ARMATURE'
    
    def execute(self, context):
        bColls = context.object.data.collections_all
        output_dict = {}
        for bColl in bColls:
            solo_set = bColl.solo_pie
            output_dict[bColl.name] = {}
            output_dict[bColl.name]['is_title'] = solo_set.is_title
            output_dict[bColl.name]['btn_icon'] = solo_set.btn_icon
            output_dict[bColl.name]['pie_wheel_enum'] = solo_set.pie_wheel_enum
            output_dict[bColl.name]['pie_row'] = solo_set.pie_row
            output_dict[bColl.name]['pie_index'] = solo_set.pie_index
            output_dict[bColl.name]['btn_label'] = solo_set.btn_label
            output_dict[bColl.name]['parent'] = None if not bColl.parent else bColl.parent.name
        with open(self.filepath, "w") as f:
            json.dump(output_dict, f, indent = 4)
        return {'FINISHED'}

class SOLOPIE_OT_preset_load(Operator, ImportHelper):
    """Load preset solo settings"""
    bl_idname = "solo_pie.preset_load"
    bl_label = "Load Settings"

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json",options={'HIDDEN'},maxlen=255)
    use_relationship: bpy.props.BoolProperty(
        name="Set Collection Parent",
        description="Set Relationship Too",
        default=True,
    )
    create_disexist: bpy.props.BoolProperty(
            name="Create Collection When No Found",
            description="Create Collection When No Found",
            default=True,
        )
    @classmethod
    def poll(cls, context):
        Obj = context.object
        if not Obj:
            return False
        return Obj.type=='ARMATURE'
    
    def execute(self, context):
        with open(self.filepath, "r") as f:
            load_data = json.load(f)
            bColls = context.object.data.collections_all
            def link_relationship():
                if not self.use_relationship:
                    return None
                collParentName = data['parent']
                collParent = None if not collParentName else bColls.get(collParentName,None)
                if not collParent :
                    return None
                bColl.parent = collParent
            def creat_new(newName):
                if not self.create_disexist:
                    return None
                return context.object.data.collections.new(newName)

            def set_bColl(bColl,data):
                if not bColl:
                    return None
                solo_set = bColl.solo_pie
                solo_set.is_title = data['is_title']
                solo_set.btn_icon = data['btn_icon']
                solo_set.pie_wheel_enum = data['pie_wheel_enum']
                solo_set.pie_row = data['pie_row']
                solo_set.pie_index = data['pie_index']
                solo_set.btn_label = data['btn_label']
                # Set Parent
                link_relationship()

                    
            for bCollName in load_data.keys():
                bColl = bColls.get(bCollName,None)
                if not bColl:
                    bColl = creat_new(bCollName)
                data = load_data.get(bCollName)
                set_bColl(bColl,data)
        return {'FINISHED'}


class SOLOPIE_OT_call_solo_pie(Operator):
    """Call Solo Pie"""
    bl_idname = "solo_pie.call_solo_pie"
    bl_label = "Call Solo Pie"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name= 'SOLOPIE_MT_pie_menu')
        return {'FINISHED'}


def bone_collection_func_import(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(ARMATURE_OT_collection_hide_all.bl_idname,text='Hide All')
    layout.operator(SOLOPIE_OT_collection_show_title_only.bl_idname,text='Show Titles Only')

# --- Register ---
classes = [
    # Pie Menu
    SOLOPIE_OT_collection_unsolo_all,
    SOLOPIE_OT_display_options,
    SOLOPIE_OT_call_solo_pie,

    # Collection Func
    SOLOPIE_OT_collection_solo,
    SOLOPIE_OT_collection_show_title_only,
    ARMATURE_OT_collection_hide_all,

    # Properties Panel
    SOLOPIE_OT_preset_save,
    SOLOPIE_OT_preset_load,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.ARMATURE_MT_collection_context_menu.append(bone_collection_func_import)
    
def unregister():
    bpy.types.ARMATURE_MT_collection_context_menu.remove(bone_collection_func_import)
    
    classes.reverse()
    for cls in classes:
        bpy.utils.unregister_class(cls)