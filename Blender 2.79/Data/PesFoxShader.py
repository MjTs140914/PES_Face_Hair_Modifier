import bpy, PES_Face_Hair_Modifier
from xml.dom.minidom import parse
from xml.dom.minidom import Node

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
	domData = parse(PES_Face_Hair_Modifier.xml_sett)
	i = 0
	material = context.material
	parameter = material.fmdl_material_parameters.clear()

	try:
		ob = bpy.context.active_object
		for slot in bpy.data.objects[ob.name].material_slots:
			materials_name = slot.name
			bpy.data.materials[materials_name].emit = 1
			mat = bpy.data.materials[materials_name]
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
							i = i + 1
							tex = bpy.data.textures.new(textures, 'IMAGE')
							texslot = bpy.data.materials[materials_name].texture_slots[i - 1]
							for idx in range(18):
								try:
									if texslot is not None:
										slot = mat.texture_slots.clear(idx)
								except:
									pass
							slot = mat.texture_slots.add()
							slot.texture = tex
							if textures == 'Base_Tex_SRGB' or textures == 'Base_Tex_LIN':
								slot.use_map_diffuse = True
								slot.use_map_color_diffuse = True
								slot.use = True
							else:
								slot.use = False
							if textures == 'NormalMap_Tex_NRM':
								bpy.context.object.active_material.texture_slots[i - 1].uv_layer = "normal_map"
							else:
								bpy.context.object.active_material.texture_slots[i - 1].uv_layer = "UVMap"
							bpy.data.textures[slot.texture.name].fmdl_texture_role = textures
							for ob in bpy.data.objects:
								for mat_slot in ob.material_slots:
									for mtex_slot in mat_slot.material.texture_slots:
										if mtex_slot:
											shaderDirpath = bpy.data.textures[mtex_slot.name].fmdl_texture_directory
											if technique == 'pes3DFW_EyeOcclusion':
												bpy.data.textures[slot.texture.name].fmdl_texture_filename = 'eye_occlusion_alp.dds'
											if technique == 'pes3DDC_Wet':
												if textures == 'CubeMap_Tex_LIN':
													bpy.data.textures[slot.texture.name].fmdl_texture_directory = '/Assets/pes16/model/character/common/sourceimages/'
													bpy.data.textures[slot.texture.name].fmdl_texture_filename = 'head_wet_cbm.dds'
												elif textures == 'NormalMap_Tex_NRM' or textures == 'SubNormalMap_Tex_NRM':
													bpy.data.textures[slot.texture.name].fmdl_texture_directory = '/Assets/pes16/model/character/common/sourceimages/'
													bpy.data.textures[slot.texture.name].fmdl_texture_filename = 'dummy_nrm.tga'
												elif textures == 'Mask_Tex_LIN':
													bpy.data.textures[slot.texture.name].fmdl_texture_directory = '/Assets/pes16/model/character/common/sourceimages/'
													bpy.data.textures[slot.texture.name].fmdl_texture_filename = 'dummy_dtm.tga'
											elif technique == 'pes3DDF_Hair2_NrmUV' or technique == 'pes3DDF_Hair2':
												if textures == 'CubeMap_Tex_LIN':
													bpy.data.textures[slot.texture.name].fmdl_texture_directory = '/Assets/pes16/model/character/common/sourceimages/'
													bpy.data.textures[slot.texture.name].fmdl_texture_filename = 'haircube_cbm.dds'
												else:
													if 'real' in shaderDirpath:
														bpy.data.textures[slot.texture.name].fmdl_texture_directory = shaderDirpath
											else:
												if 'real' in shaderDirpath:
													bpy.data.textures[slot.texture.name].fmdl_texture_directory = shaderDirpath

					for vector in foxshader:
						if vector.getAttribute("vector"):
							parameter = material.fmdl_material_parameters.add()
							parameter.name = vector.getAttribute("vector")
							parameter.parameters = [float(vector.getAttribute("xValue")),float(vector.getAttribute("yValue")), float(vector.getAttribute("zValue")), float(vector.getAttribute("wValue"))]
					domData.unlink()
		self.report({"INFO"}, "Shader has been set!!")
	except:
		self.report({"WARNING"}, "Error when set shader!!")
		return {'CANCELLED'}
	return 1