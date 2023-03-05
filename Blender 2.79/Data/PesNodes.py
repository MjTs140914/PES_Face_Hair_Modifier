import bpy, random, re, os
from . import IO, Ftex
from mathutils import Vector



def findTexture(texture, textureSearchPath):
	textureFilename = texture.directory.replace('\\', '/').rstrip('/') + '/' + texture.filename.replace('\\', '/').lstrip('/')
	textureFilenameComponents = tuple(filter(None, textureFilename.split('/')))

	if len(textureFilenameComponents) == 0:
		return None
	filename = textureFilenameComponents[-1]
	directory = textureFilenameComponents[:-1]
	directorySuffixes = [directory[i:] for i in range(len(directory) + 1)]
	
	if filename == 'kit.dds':
		filenames = []
	else:
		filenames = [filename]
		position = filename.rfind('.')
		if position >= 0:
			for extension in ['dds', 'tga', 'ftex']:
				modifiedFilename = filename[:position + 1] + extension
				if modifiedFilename not in filenames:
					filenames.append(modifiedFilename)
	
	for searchDirectory in textureSearchPath:
		for suffix in directorySuffixes:
			for filename in filenames:
				fullFilename = os.path.join(searchDirectory, *suffix, filename)
				if os.path.isfile(fullFilename):
					return fullFilename
			
			if len(filenames) == 0:
				directory = os.path.join(searchDirectory, *suffix)
				
				if not os.path.isdir(directory):
					continue
				
				try:
					entries = os.listdir(directory)
				except:
					continue
				for entry in entries:
					if re.match('^u[0-9]{4}p1\.dds$', entry, flags = re.IGNORECASE):
						fullFilename = os.path.join(directory, entry)
						if os.path.isfile(fullFilename):
							print(entry)
							return fullFilename
	
	return None

def createNodes(blenderMaterial):
	 #Only one time create get exception from TRM Subsurface, and will create in exception
	try:
		blenderMaterial.node_tree.nodes.get('TRM Subsurface').name
	except:
		new_group_node = blenderMaterial.node_tree.nodes.new('ShaderNodeGroup')
		new_group_node.node_tree = bpy.data.node_groups['TRM Subsurface']
		blenderMaterial.node_tree.nodes['Group'].name = 'TRM Subsurface'
		new_group_node = blenderMaterial.node_tree.nodes.new('ShaderNodeGroup')
		new_group_node.node_tree = bpy.data.node_groups['SRM Seperator']
		blenderMaterial.node_tree.nodes['Group'].name = 'SRM Seperator'
		new_group_node = blenderMaterial.node_tree.nodes.new('ShaderNodeGroup')
		new_group_node.node_tree = bpy.data.node_groups['NRM Converter']
		blenderMaterial.node_tree.nodes['Group'].name = 'NRM Converter'

def addTexture(context, blenderMaterial, textureRole, texture, textureIDs, uvMapColor, uvMapNormals, textureSearchPath, loadTextures):

	blenderMaterial.use_nodes = True
	identifier = (textureRole, texture)
	texture_path = context.scene.face_path[:-29] + "\\sourceimages\\#windx11\\" + texture.filename
	textureName=textureRole
	textureLabel=texture.filename
	if identifier in textureIDs:
		blenderTexture = blenderMaterial.node_tree.get(textureIDs[identifier])
	else:
		if textureLabel in bpy.data.images:
			blenderImage = bpy.data.images[texture.filename]
		else:
			blenderImage = bpy.data.images.new(texture.filename, width=0, height=0)
		blenderImage.source = 'FILE'
		createNodes(blenderMaterial)

		if '_SRGB' in textureRole:
			blenderImage.colorspace_settings.name = 'sRGB'
		elif '_LIN' in textureRole:
			blenderImage.colorspace_settings.name = 'Linear'
		else:
			blenderImage.colorspace_settings.name = 'Non-Color'

		filename = findTexture(texture, textureSearchPath)
		if filename is None:
			blenderImage.filepath = texture_path
		elif filename.lower().endswith('.ftex'):
			blenderImage.filepath = filename
			Ftex.blenderImageLoadFtex(blenderImage, bpy.app.tempdir)
		else:
			blenderImage.filepath = filename
			blenderImage.reload()
			
		if 'pes3DDF_Skin_Face' in blenderMaterial.fmdl_material_technique:
			blenderMaterial.use_sss_translucency = True
		if 'pes3DDF_Hair' in blenderMaterial.fmdl_material_technique:
			blenderMaterial.blend_method = 'HASHED'
		elif 'pes3DDC_Adjust' in blenderMaterial.fmdl_material_technique:
			blenderMaterial.blend_method = 'CLIP'
			blenderMaterial.alpha_threshold = 1.0
		elif 'fox3DDC_Blin' in blenderMaterial.fmdl_material_technique:
			blenderMaterial.blend_method = 'BLEND'
			blenderMaterial.show_transparent_back = True
		elif 'fox3DDF_Blin_Translucent' in blenderMaterial.fmdl_material_technique:
			blenderMaterial.blend_method = 'BLEND'
			blenderMaterial.show_transparent_back = False
		else:
			blenderMaterial.blend_method = 'BLEND'
			blenderMaterial.show_transparent_back = False
			
		blenderTexture = blenderMaterial.node_tree.nodes.new("ShaderNodeTexImage")
		blenderTexture.fmdl_texture_filename = blenderImage.filepath

		blenderTexture.fmdl_texture_directory = texture.directory

		blenderTexture.fmdl_texture_role = textureRole
		blenderTexture.name = textureName
		blenderTexture.label = textureLabel
		blenderTexture.image = blenderImage
		principled = blenderMaterial.node_tree.nodes['Principled BSDF']

		rdmx = random.randint(-500, 400)
		rdmy = random.randint(-400, 300)
		blenderImage.alpha_mode = 'STRAIGHT'
		if 'face_bsm' in textureLabel:
			blenderImage.alpha_mode = 'NONE'
		blenderTexture.select = True
		blenderMaterial.node_tree.nodes.active = blenderTexture
		TRM_Subsurface = blenderMaterial.node_tree.nodes['TRM Subsurface']
		TRM_Subsurface.location = Vector((-200, 200))
		SRM_Seperator = blenderMaterial.node_tree.nodes['SRM Seperator']
		SRM_Seperator.location = Vector((-200, 0))
		NRM_Converter = blenderMaterial.node_tree.nodes['NRM Converter']
		NRM_Converter.location = Vector((-200, -200))
		blenderMaterial.node_tree.links.new(TRM_Subsurface.outputs['Subsurface'], principled.inputs['Subsurface'])
		blenderMaterial.node_tree.links.new(TRM_Subsurface.outputs['Subsurface Color'], principled.inputs['Subsurface Color'])
		blenderMaterial.node_tree.links.new(SRM_Seperator.outputs['Specular'], principled.inputs['Specular'])
		blenderMaterial.node_tree.links.new(SRM_Seperator.outputs['Roughness'], principled.inputs['Roughness'])
		blenderMaterial.node_tree.links.new(NRM_Converter.outputs['Normal'], principled.inputs['Normal'])
		if 'Base_Tex_SRGB' in textureRole or 'Base_Tex_LIN' in textureRole:
			blenderTexture.location = Vector((-500, 560))
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], principled.inputs['Base Color'])
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], TRM_Subsurface.inputs['BSM Tex'])
			if blenderImage.alpha_mode != 'NONE':
				blenderMaterial.node_tree.links.new(blenderTexture.outputs['Alpha'], principled.inputs['Alpha'])
			if 'pes3DDF_Hair' in blenderMaterial.fmdl_material_technique:
				blenderMaterial.node_tree.links.new(blenderTexture.outputs['Alpha'], principled.inputs['Alpha'])
		elif 'NormalMap_Tex_' in textureRole:
			blenderTexture.location = Vector((-500, -220))
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], NRM_Converter.inputs['NRM Tex'])
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Alpha'], NRM_Converter.inputs['Alpha'])
		elif 'SpecularMap_Tex_' in textureRole:
			blenderTexture.location = Vector((-500, 40))
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], SRM_Seperator.inputs['SRM Tex'])
		elif 'RoughnessMap_Tex_' in textureRole:
			blenderTexture.location = Vector((-750, 40))
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], SRM_Seperator.inputs['RGM Tex'])
		elif 'Translucent_Tex_' in textureRole:
			blenderTexture.location = Vector((-500, 300))
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], TRM_Subsurface.inputs['TRM Tex'])
		elif 'MetalnessMap_Tex_' in textureRole:
			blenderMaterial.node_tree.links.new(blenderTexture.outputs['Color'], principled.inputs['Metallic'])
			blenderTexture.location = Vector((-750, 0))
		else:
			blenderTexture.location = Vector((rdmx, rdmy))

	if blenderTexture is not None:
		blenderTexture.fmdl_texture_filename = texture.filename
		blenderTexture.fmdl_texture_directory = texture.directory
		blenderTexture.fmdl_texture_role = textureRole

	for nodes in blenderMaterial.node_tree.nodes:
		nodes.select = False 