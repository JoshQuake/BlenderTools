import bpy
from send2ue.core import utilities
from send2ue.constants import ToolInfo
from send2ue.core.extension import ExtensionBase

hair_object_copies = []

# Get or create temp collection (necessary?) 
def get_temp_collection(collection_name="GroomTempCollection"):
    if collection_name in bpy.data.collections:
        temp_collection = bpy.data.collections[collection_name]
    else:
        temp_collection = bpy.data.collections.new(name=collection_name)
        bpy.context.scene.collection.children.link(temp_collection)
    
    return temp_collection

# make copies of original objects, link to temp collection, and store for removal later
# Now that I think about it, storing isn't necessary since I can just grab objects from temp collection
# I will change later - JoshQuake
def apply_groom_modifiers():
    properties = bpy.context.scene.send2ue
    hair_objects = utilities.get_hair_objects(properties)
    temp_collection = get_temp_collection()

    hair_object_copies.clear()

    for hair_object in hair_objects:
        hair_copy = hair_object.copy()
        hair_copy.data = hair_object.data.copy()
        temp_collection.objects.link(hair_copy)
        hair_object_copies.append(hair_copy)

        for modifier in hair_object.modifiers:
            bpy.context.view_layer.objects.active = hair_object
            print(modifier.name)
            if modifier.name != 'Surface Deform':
                bpy.ops.object.modifier_apply(modifier=modifier.name)

# Delete modified objects and restore original copies
def restore_groom_modifiers():
    temp_collection = get_temp_collection()
    export_collection = bpy.data.collections.get(ToolInfo.EXPORT_COLLECTION.value)

    for hair_copy in hair_object_copies:
        original_name = hair_copy.name.split(".")[0]
        modified_hair_object = bpy.data.objects.get(original_name)
        if modified_hair_object:
            bpy.data.objects.remove(modified_hair_object, do_unlink=True)
            export_collection.objects.link(hair_copy)
            temp_collection.objects.unlink(hair_copy)
            hair_copy.name = original_name

    hair_object_copies.clear()
    bpy.data.collections.remove(temp_collection)

class ApplyGroomModifiersExtension(ExtensionBase):
    name = 'applygroommodifiers'

    apply_groom_mods: bpy.props.BoolProperty(
        name= "Apply Groom Mods",
        default= False,
        description="Automatically applies hair modifiers for export "
                    "Modifiers restored after export finishes."
    )

    # Draws setting in extensions panel.
    def draw_export(self, dialog, layout, properties):
        box = layout.box()
        box.label(text='Groom Modifiers:')
        dialog.draw_property(self, box, 'apply_groom_mods')

    def pre_operation(self, properties):
        if self.apply_groom_mods:
            print('groommods enabled')
            apply_groom_modifiers()

    def post_operation(self, properties):
        if self.apply_groom_mods:
            print('groommods post')
            restore_groom_modifiers()