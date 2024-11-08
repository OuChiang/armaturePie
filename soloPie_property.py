import bpy
from bpy.types import PropertyGroup

pie_wheel_directions = [ "Left","Right", "Down", "Up", "Left Up", "Right Up", "Left Down", "Right Down"]

class BONECOLLECTION_PG_soloPie(PropertyGroup):
    #Solo Settings
    is_title: bpy.props.BoolProperty(
        default=False,
        description='Set bone collection is title',
        )
    btn_icon: bpy.props.StringProperty(
        default='BLANK1',
        description='The icon you want to show in solo pie',
        )
    btn_label: bpy.props.StringProperty(
        default='',
        description='The name you want to show in solo pie',
        )

    layout_items = [(str(i),pie_wheel_directions[i],pie_wheel_directions[i],i ) for i in range(0,8)]
    pie_wheel_enum : bpy.props.EnumProperty(items = layout_items ,default = '0')
    pie_row: bpy.props.IntProperty(default=0,min=0)
    pie_index: bpy.props.IntProperty(default=0,min=0)


class ARMATURE_PG_soloPie(PropertyGroup):
    active_idx : bpy.props.IntProperty(default = 0)

def weightBone_search_poll(self, object):
    return object.type =='ARMATURE'


class SCENE_PG_soloPie(PropertyGroup):
    show_use_active : bpy.props.BoolProperty(
        description='Solo pie menu shows actived object or specific object',
        default = True,
        )

    armature : bpy.props.PointerProperty(
        description='Specific object for solo pie menu',
        type=bpy.types.Object,
        poll=weightBone_search_poll
        )



def register():
    bpy.utils.register_class(SCENE_PG_soloPie)
    bpy.utils.register_class(BONECOLLECTION_PG_soloPie)
    bpy.utils.register_class(ARMATURE_PG_soloPie)
    bpy.types.Scene.solo_pie =  bpy.props.PointerProperty(type=SCENE_PG_soloPie)
    bpy.types.BoneCollection.solo_pie =  bpy.props.PointerProperty(type=BONECOLLECTION_PG_soloPie)
    bpy.types.Armature.solo_pie =  bpy.props.PointerProperty(type=ARMATURE_PG_soloPie)

def unregister():
    del bpy.types.Armature.solo_pie
    del bpy.types.BoneCollection.solo_pie
    del bpy.types.Scene.solo_pie
    bpy.utils.unregister_class(ARMATURE_PG_soloPie)    
    bpy.utils.unregister_class(BONECOLLECTION_PG_soloPie)
    bpy.utils.unregister_class(SCENE_PG_soloPie)
