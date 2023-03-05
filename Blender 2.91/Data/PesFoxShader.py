import bpy, PES_Face_Hair_Modifier
from xml.dom.minidom import parse
from xml.dom.minidom import Node

AlphaEnum = [('Unknown', 'Unknown', 'Unknown'),
			('0', 'No Alpha', 'No Alpha'),
			('16', 'Glass', 'Glass'),
			('17', 'Glass2', 'Glass2'),
			('48', 'Glass3', 'Glass3'),
			('49', 'Glass4', 'Glass4'),
			('80', 'Decal', 'Decal'),
			('81', 'Decal2', 'Decal2'),
			('112', 'Eyelash', 'Eyelash'),
			('113', 'Eyelash2', 'Eyelash2'),
			('128', 'Parasite', 'Parasite'),
			('140', 'Alpha2', 'Alpha2'),
			('160', 'Alpha', 'Alpha'),
			('192', 'Unknown OMBS', 'Unknown OMBS'),
			('32', 'No backface culling', 'No backface culling')
]
ShadowEnum = [('Unknown', 'Unknown', 'Unknown'),
			('0', 'Shadow', 'Shadow'),
			('1', 'No Shadow', 'No Shadow'),
			('2', 'Invisible Mesh Visible Shadow', 'Invisible Mesh Visible Shadow'),
			('4', 'Tinted Glass', 'Tinted Glass'),
			('5', 'Glass', 'Glass'),
			('36', 'Light OMBS', 'Light OMBS'),
			('37', 'Glass OMBS', 'Glass OMBS'),
			('64', 'Shadow2', 'Shadow2'),
			('65', 'No Shadow2', 'No Shadow2')
]

parent_list = [('MESH_face_high', 'MESH_face_high', 'Move selected object to MESH_face_high'),
			('MESH_face_parts', 'MESH_face_parts', 'Move selected object to MESH_face_parts'),
			('MESH_hair_high', 'MESH_hair_high', 'Move selected object to MESH_hair_high')
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
				technique = shader.getAttribute("technique")	
				if shaderfox == getshader:
					bpy.data.materials[materials_name].fmdl_material_shader = shaderfox
					bpy.data.materials[materials_name].fmdl_material_technique = technique	
					foxshader = shader.getElementsByTagName("Parameter")
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