import bpy, PES_Face_Hair_Modifier
from xml.dom.minidom import parse
from xml.dom.minidom import Node
from mathutils import Vector
import random

			#format: ('shader', 'shader', 'technique')
ShaderList = [('pes_3ddf_skin_face', 'pes_3ddf_skin_face', 'pes3DDF_Skin_Face'),
			('pes3ddc_wet', 'pes3ddc_wet', 'pes3DDC_Wet'), 
            ('pes_3ddc_wet', 'pes_3ddc_wet', 'pes3DDC_Wet'), 
			('pes_3ddc_adjust', 'pes_3ddc_adjust', 'pes3DDC_Adjust_100'),
			('fox3ddf_blin_4mt_subnorm', 'fox3ddf_blin_4mt_subnorm', 'fox3DDF_Blin_SubNorm_4MT'),
			('fox3ddf_blin', 'fox3ddf_blin', 'fox3DDF_Blin'),
			('fox3ddf_blin_ln', 'fox3ddf_blin_ln', 'fox3DDF_Blin_LNM'),
			('fox3dfw_blin_ln', 'fox3dfw_blin_ln', 'fox3DDF_Blin_LNM'),
			('pes_3ddf_hair2_nrmuv', 'pes_3ddf_hair2_nrmuv', 'pes3DDF_Hair2_NrmUV'),
            ('pes_3ddf_hair2', 'pes_3ddf_hair2', 'pes3DDF_Hair2'),
			('pes_3dfw_eyeocclusion', 'pes_3dfw_eyeocclusion', 'pes3DFW_EyeOcclusion'),
			('fox_3ddf_ggx_nrmuv', 'fox_3ddf_ggx_nrmuv', 'fox3DDF_GGX'),
			('pes_3dfw_glass2', 'pes_3dfw_glass2', 'pes3DFW_Glass2'),
			('pes_3dfw_const_srgb_bill', 'pes_3dfw_const_srgb_bill', 'pes3DFW_Constant_SRGB_Bill')
			   
]

def setShader(self, context):
	get_texture_directory = str()
	domData = parse(PES_Face_Hair_Modifier.xml_sett)
	material = context.material
	parameter = material.fmdl_material_parameters.clear()
	blenderMaterial = bpy.context.active_object.active_material
	blenderMaterial.node_tree.nodes.clear()
	blenderOutput = blenderMaterial.node_tree.nodes.new("ShaderNodeOutputMaterial")
	blenderOutput.location = Vector((400, 200))
	blenderShader = blenderMaterial.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
	blenderShader.location = Vector((0, 200))
	Material_Output = blenderMaterial.node_tree.nodes['Material Output']
	blenderMaterial.node_tree.links.new(blenderShader.outputs['BSDF'], Material_Output.inputs['Surface'])
	try:
		for matname in bpy.data.materials:
			try:
				for ndname in bpy.data.materials[matname.name].node_tree.nodes:
					if ndname is not None:
						if 'Base_Tex_' in ndname.name:
							texture_directory = bpy.data.materials[matname.name].node_tree.nodes[ndname.name].fmdl_texture_directory
							if 'real' in texture_directory:
								get_texture_directory = texture_directory
			except:
				pass
		ob = bpy.context.active_object
		for slot in bpy.data.objects[ob.name].material_slots:
			materials_name = slot.name
			getshader = bpy.data.materials[materials_name].fox_shader
			fox = domData.getElementsByTagName("FoxShader")
			for shader in fox:
				shaderfox = shader.getAttribute("shader")
				if shaderfox == getshader:
					bpy.data.materials[materials_name].fmdl_material_shader = shaderfox
					foxshader = shader.getElementsByTagName("Parameter")
					for fox_shader in foxshader:
						if fox_shader.getAttribute("technique"):
							technique = fox_shader.getAttribute("technique")
							bpy.data.materials[materials_name].fmdl_material_technique = technique
					for texture in foxshader:
						textures = texture.getAttribute("textures")
						if textures:
							rdmx = random.randint(-500, 400)
							rdmy = random.randint(-400, 300)
							blenderTexture = blenderMaterial.node_tree.nodes.new("ShaderNodeTexImage")
							blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_role = textures
							blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_directory = get_texture_directory

							if technique == 'pes3DFW_EyeOcclusion':
								blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_filename  = 'eye_occlusion_alp.dds'
							if technique == 'pes3DDC_Wet':
								if textures == 'CubeMap_Tex_LIN':
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_directory = '/Assets/pes16/model/character/common/sourceimages/'
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_filename = 'head_wet_cbm.dds'
								elif textures == 'NormalMap_Tex_NRM' or textures == 'SubNormalMap_Tex_NRM':
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_directory = '/Assets/pes16/model/character/common/sourceimages/'
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_filename = 'dummy_nrm.tga'
								elif textures == 'Mask_Tex_LIN':
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_directory ='/Assets/pes16/model/character/common/sourceimages/'
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_filename = 'dummy_dtm.tga'
							elif technique == 'pes3DDF_Hair2_NrmUV' or technique == 'pes3DDF_Hair2':
								if textures == 'CubeMap_Tex_LIN':
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_directory = '/Assets/pes16/model/character/common/sourceimages/'
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_filename = 'haircube_cbm.dds'
								else:
									if 'real' in get_texture_directory:
										blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_directory = get_texture_directory
							else:
								if 'real' in get_texture_directory:
									blenderMaterial.node_tree.nodes['Image Texture'].fmdl_texture_directory = get_texture_directory

							blenderMaterial.node_tree.nodes['Image Texture'].name = textures
							principled = blenderMaterial.node_tree.nodes['Principled BSDF']
							
							
							blenderTexture.select = True
							blenderMaterial.node_tree.nodes.active = blenderTexture
						
							if 'Base_Tex_' in textures:
								blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], principled.inputs['Base Color'])
								blenderTexture.location = Vector((-300, 300))
							elif 'NormalMap_Tex_' in textures:
								blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], principled.inputs['Normal'])
								blenderTexture.location = Vector((300, 0))
							elif 'SpecularMap_Tex_' in textures:
								blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], principled.inputs['Specular'])
								blenderTexture.location = Vector((-300, 50))
							elif 'RoughnessMap_Tex_' in textures:
								blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], principled.inputs['Roughness'])
								blenderTexture.location = Vector((-300, -200))
							elif 'MetalnessMap_Tex_' in textures:
								blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], principled.inputs['Metallic'])
								blenderTexture.location = Vector((-300, -400))
							else:
								blenderTexture.location = Vector((rdmx, rdmy))

					for vector in foxshader:
						if vector.getAttribute("vector"):
							parameter = material.fmdl_material_parameters.add()
							parameter.name = vector.getAttribute("vector")
							parameter.parameters = [float(vector.getAttribute("xValue")),float(vector.getAttribute("yValue")), float(vector.getAttribute("zValue")), float(vector.getAttribute("wValue"))]
					domData.unlink()
					for nodes in blenderMaterial.node_tree.nodes:
						nodes.select = False
		
		self.report({"INFO"}, "Shader has been set!!")
	except IOError:
		self.report({"WARNING"}, "Error when set shader!!")
		return {'CANCELLED'}
	return 1