import bpy
from mathutils import Vector, Matrix
from bpy.types import Operator, AddonPreferences
from bpy.props import FloatProperty, BoolProperty, EnumProperty, PointerProperty

class FMDL_21_PT_TransferNormalsPanel(bpy.types.Panel):
    bl_label = "Normals"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_context = "objectmode"

    def draw(self, context):
        panel = self.layout.column(align=True)
        panel.operator("object.transfer_normals", text="Transfer Normals")
        panel.operator("object.wrap_normals", text="Wrap Normals")
        panel.operator("object.clear_normals", text="Clear Normals")


def group_items(scene, context):

    items = [('NONE', "None", '', '', 0)]
    target = context.active_object
    
    selection = bpy.context.selected_objects
    for ob in selection:
        if ob.type != 'MESH':
            selection.remove(ob)
            
    global tina_to_active
    if not tina_to_active and len(selection) is 2:
        for ob in selection:
            if ob != target:
                target = ob
    
    for g in target.vertex_groups:
        group_item = (g.name, g.name, '', 'GROUP_VERTEX', g.index + 1)
        items.append(group_item)
        
    return items

class FMDL_TransferNormals(bpy.types.Operator):
    """Transfers normals between selected and active meshes"""
    bl_idname = "object.transfer_normals"
    bl_label = "Transfer Normals"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    
    to_active : bpy.props.BoolProperty(name="To Active", default = True, description="Transfer from selection to active object")
    transfer_vcol : bpy.props.BoolProperty(name="Vertex Colors", default = True, description="Transfer vertex colors as well")
    use_distance : bpy.props.BoolProperty(name="Use Max Distance", default = True, description="Use maximum distance")
    max_distance : bpy.props.FloatProperty(name="Max Distance", default = 0.01, min = 0, max = 1000)
    mix_factor : bpy.props.FloatProperty(name="Mix Factor", default = 1.0, min = 0, max = 1)
    group : bpy.props.EnumProperty(name="Vertex Group", items=group_items, description="Vertex Group")

    def draw(self, context):
        panel = self.layout.column()
        
        first_row = panel.row()
        first_row.prop(self, "to_active")
        first_row.prop(self, "transfer_vcol", toggle=True, icon='GROUP_VCOL', text="")
        
        second_row = panel.row()
        check_col = second_row.column()
        check_col.prop(self, "use_distance", text="")
        mixmax_col = second_row.column()
        dist_row = mixmax_col.row()
        dist_row.prop(self, "max_distance")
        dist_row.enabled = self.use_distance
        mix_row = mixmax_col.row()
        mix_row.prop(self, "mix_factor")
                
        selection = bpy.context.selected_objects;
        for ob in selection:
            if ob.type != "MESH":
                selection.remove(ob)
                                                
        global tina_to_active
        if tina_to_active or len(selection) is 2:                
            panel.label(icon='GROUP_VERTEX', text="Vertex Group:")
            panel.prop(self, "group", text="")

    def execute(self, context):
        global tina_to_active
        tina_to_active = self.to_active
        
        data_types = {'CUSTOM_NORMAL'}
        if self.transfer_vcol:
            data_types.add('VCOL')
        
        active = bpy.context.active_object
        if active.type != "MESH":
            self.report({'ERROR'}, "Active object must have mesh data")
            return {'CANCELLED'}

        selection = bpy.context.selected_objects;
        for ob in selection:
            if ob.type != "MESH":
                selection.remove(ob)
                            
        if len(selection) < 2:
            self.report({'ERROR'}, "Select multiple mesh objects")
# WrapNormals
            return {'CANCELLED'}
        
# Transfer normals from or to selection        
        for ob in selection:
            if active != ob and ob.type == "MESH":
                
                target = active if self.to_active else ob
                source = ob     if self.to_active else active
                
                bpy.ops.object.select_all(action='DESELECT')
                target.select_set(True)
                bpy.ops.object.duplicate()
                duplicate = bpy.context.selected_objects[0]
                duplicate.modifiers.clear()
                
                if not duplicate.data.use_auto_smooth:
                    duplicate.data.auto_smooth_angle = 3.14159
                    duplicate.data.use_auto_smooth = True
                
                transfer = duplicate.modifiers.new(source.name, 'DATA_TRANSFER')
                transfer.object = source
                transfer.use_loop_data = True
                transfer.data_types_loops = data_types
                transfer.loop_mapping = 'NEAREST_POLYNOR'
                transfer.use_max_distance = self.use_distance
                transfer.max_distance = self.max_distance
                transfer.mix_factor = self.mix_factor
                
                #Fails when there is a group named NONE, PointerProperty could fix this
                if self.to_active or len(selection) is 2:
                    transfer.vertex_group = self.group
                
                bpy.context.view_layer.objects.active = duplicate
                bpy.ops.object.modifier_apply(modifier=transfer.name)
                ##### Replace data and remove duplicate         
                duplicate.data.name = target.data.name
                for ob in bpy.context.view_layer.objects:
                    if ob.data == target.data and ob != target:
                        ob.data = duplicate.data
                old_data = target.data
                target.data = duplicate.data
                bpy.ops.object.select_all(action='DESELECT')
                duplicate.select_set(True)
                bpy.ops.object.delete()
                bpy.data.meshes.remove(old_data)

        # Restore selection
        for ob in selection:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = active
        
        return {'FINISHED'}
    
class FMDL_WrapNormals(bpy.types.Operator):    
    """Make normals continuous"""
    bl_idname = "object.wrap_normals"
    bl_label = "Wrap Normals"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"

    wrap_x : bpy.props.BoolProperty(name="X", default = True, description="Wrap normals along X-axis")
    wrap_y : bpy.props.BoolProperty(name="Y", default = True, description="Wrap normals along Y-axis")
    wrap_z : bpy.props.BoolProperty(name="Z", default = True, description="Wrap normals along Z-axis")
    offset_x : bpy.props.FloatProperty(name="Offset", default = 1.0, min = 0, max = 1000)
    offset_y : bpy.props.FloatProperty(name="Offset", default = 1.0, min = 0, max = 1000)
    offset_z : bpy.props.FloatProperty(name="Offset", default = 1.0, min = 0, max = 1000)
    group : bpy.props.EnumProperty(name="Vertex Group", items=group_items, description="Vertex Group")
    transfer_vcol : bpy.props.BoolProperty(name="Vertex Colors", default = True, description="Wrap vertex colors as well")
    
    def draw(self, context):

        panel = self.layout.column()
    
        x_row = panel.row()
        wxc = x_row.column()
        wxc.scale_x = 0.17
        wxc.prop(self, "wrap_x", toggle=True)
        x_column = x_row.column()
        x_column.prop(self, "offset_x")
        x_column.enabled = self.wrap_x
        
        y_row = panel.row()
        wyc = y_row.column()
        wyc.scale_x = 0.17
        wyc.prop(self, "wrap_y", toggle=True)
        y_column = y_row.column()
        y_column.prop(self, "offset_y")
        y_column.enabled = self.wrap_y
        
        z_row = panel.row()
        wzc = z_row.column()
        wzc.scale_x = 0.17
        wzc.prop(self, "wrap_z", toggle=True)
        z_column = z_row.column()
        z_column.prop(self, "offset_z")
        z_column.enabled = self.wrap_z
        
        panel.label(icon='GROUP_VERTEX', text="Vertex Group:")
        group_row = panel.row()
        group_row.prop(self, "group", text="")
        group_row.prop(self, "transfer_vcol", toggle=True, icon='GROUP_VCOL', text="")
        
    def execute(self, context):
        
        data_types = {'CUSTOM_NORMAL'}
        if self.transfer_vcol:
            data_types.add('VCOL')
        
        active = bpy.context.object
        if active.type != "MESH":
            self.report({'ERROR'}, "Active object must have mesh data")
            return {'CANCELLED'}
        
        selection = bpy.context.selected_objects
        ## Duplicate active object to have single-user data
        bpy.ops.object.select_all(action='DESELECT')
        active.select_set(True)
        bpy.ops.object.duplicate()
        target = bpy.context.selected_objects[0]
        target.modifiers.clear()
        ## Create merged array to transfer normals from
        bpy.ops.object.duplicate()
        source = bpy.context.selected_objects[0]
        
        axes = []
        offset = Vector((0.0, 0.0, 0.0))
        if self.wrap_x:
            axes.append('X')
            offset[0] -= self.offset_x
        if self.wrap_y:
            axes.append('Y')
            offset[1] -= self.offset_y
        if self.wrap_z:
            axes.append('Z')
            offset[2] -= self.offset_z

        offset = active.matrix_world.to_3x3() @ offset
        source.location = source.location + offset
        for axis in axes:
            array = source.modifiers.new(axis, 'ARRAY')
            array.count = 3
            array.use_constant_offset = True
            array.use_relative_offset = False
            array.use_merge_vertices = True
            array.merge_threshold = 0.01
            array.constant_offset_displace = [
                self.offset_x if axis is 'X' else 0,
                self.offset_y if axis is 'Y' else 0,
                self.offset_z if axis is 'Z' else 0
            ]
        while len(source.modifiers):    
            bpy.ops.object.modifier_apply(modifier=source.modifiers[0].name)
            
        ## Transfer normals
        bpy.ops.object.select_all(action='DESELECT')
        source.select_set(True)
        target.select_set(True)
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.transfer_normals(
            to_active = True,
            use_distance = True,
            max_distance = 0.01,
            mix_factor = 1.0,
            transfer_vcol = self.transfer_vcol
        )
        
        ## Replace data
        target.data.name = active.data.name
        for ob in bpy.context.view_layer.objects:
            if ob.data == active.data and ob != active:
                ob.data = target.data
        old_data = active.data
        active.data = target.data
        
        ## Remove temporary source and target objects and restore selection
        bpy.ops.object.delete()
        bpy.data.meshes.remove(old_data)
        for ob in selection:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = active
        
        return {'FINISHED'}

class FMDL_ClearNormals(bpy.types.Operator):
    """Clear custom normals data for entire selection"""
    bl_idname = "object.clear_normals"
    bl_label = "Clear Custom Normals"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"

    def execute(self, context):
        
        active = bpy.context.active_object
        
        for ob in bpy.context.selected_objects:
            if ob.type == "MESH":
                bpy.context.view_layer.objects.active = ob
                bpy.ops.mesh.customdata_custom_splitnormals_clear()

        bpy.context.view_layer.objects.active = active
        return {'FINISHED'}
