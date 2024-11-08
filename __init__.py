import bpy
from . import armature_picker
from . import soloPie_property
from . import soloPie_operator
from . import soloPie_panel
from . import keymap_settings
class_list = [
    armature_picker,
    soloPie_property,
    soloPie_operator,
    soloPie_panel,
    keymap_settings
    ]

def register():
    for cls in class_list:
        cls.register()

def unregister():
    class_list.reverse()
    for cls in class_list:
        cls.unregister()
