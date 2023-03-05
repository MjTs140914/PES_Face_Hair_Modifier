import bpy, os, fnmatch, binascii, bmesh, shutil, os.path, struct, bpy.props, bpy_extras.io_utils, re, bpy.utils.previews
from struct import *
from bpy.props import *
from Data import FmdlFile, Ftex, IO, PesSkeletonData, TiNA, PesFoxShader
from configparser import ConfigParser
from bpy.props import (IntProperty, BoolProperty, StringProperty, FloatProperty, CollectionProperty)
from xml.dom import minidom
from xml.dom.minidom import parse

config = ConfigParser()
icons_collections = {}

bl_info = {
	"name": "PES Face/Hair Modifier",
	"author": "the4chancup - MjTs-140914",
	"version": (1, 93, 7),
	"blender": (2, 79, 0),
	"api": 35853,
	"location": "Under Scene Tab",
	"description": "PES Face/Hair Modifier",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "System"
}

AddonsPath = str()
AddonsPath = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
GZSPATH = '"%s\\addons\\Data\\Gzs\\GzsTool.exe"' % AddonsPath 
FtexTools ='"%s\\addons\\Data\\Gzs\\FtexTools.exe"' % AddonsPath 
texconvTools = '"%s\\addons\\Data\\Gzs\\texconv.exe"' % AddonsPath 
ini_sett = '%s\\addons\\Data\\Gzs\\Settings.ini' % AddonsPath
xml_sett = '%s\\addons\\Data\\Gzs\\PesFoxShader.xml' % AddonsPath
icons_dir = '%s\\addons\\Data\\Gzs\\icons' % AddonsPath
base_file_blend = '%s\\addons\\Data\\Gzs\\base_file.blend' % AddonsPath

pes_diff_bin_data, IDoldname = [] , []
eyeL_origin, eyeR_origin, mouth_origin = [0.02807705,0.1448301-0.00362,1.69668636147], [0.02754705,0.1446231-0.00362,1.69682636147], [-0.000365,0.1479722561,1.63275]

def scene_objects():
	inner_path = 'Object'
	for ob_name in ('eyeL', 'eyeR', 'mouth'):
		if not ob_name in bpy.data.objects:
			bpy.ops.wm.append(filepath=os.path.join(base_file_blend, inner_path, ob_name), directory=os.path.join(base_file_blend, inner_path), filename=ob_name)

def pes_diff_bin_imp(pes_diff_fname):
	global pes_diff_bin_data
	scn = bpy.context.scene
	facepath = scn.face_path
	oralpath = facepath[:-14] + "oral.fmdl"
	scene_objects()
	header_data = open(pes_diff_fname, 'rb').read(4)
	header_string = str(header_data, "utf-8")
	if header_string == "FACE":
		pes_diff_data0 = open(pes_diff_fname, "rb")
		pes_diff_data0.seek(0x08)
		eyes_size = unpack("3f", pes_diff_data0.read(12))
		pes_diff_data0.seek(0x3c)
		m_pos = unpack("3f", pes_diff_data0.read(12))
		pes_diff_data0.seek(0x150)
		eyes_posR = unpack("3f", pes_diff_data0.read(12))
		pes_diff_data0.seek(0x160)
		eyes_posL = unpack("3f", pes_diff_data0.read(12))

		scn.eyes_size = eyes_size[0]


		if not os.path.isfile(oralpath): 
			bpy.data.objects['mouth'].location[0] = (m_pos[0]) - mouth_origin[0]
			bpy.data.objects['mouth'].location[1] = (m_pos[2]*-1) - mouth_origin[1]
			bpy.data.objects['mouth'].location[2] = (m_pos[1]) + mouth_origin[2]

		bpy.data.objects['eyeR'].location[0] = (eyes_posR[2] * -1) - eyeR_origin[0]
		bpy.data.objects['eyeR'].location[1] = (eyes_posR[1]) - eyeR_origin[1]
		bpy.data.objects['eyeR'].location[2] = (eyes_posR[0]) + eyeR_origin[2]

		bpy.data.objects['eyeL'].location[0] = (eyes_posL[2]*-1) + eyeL_origin[0]
		bpy.data.objects['eyeL'].location[1] = (eyes_posL[1]) - eyeL_origin[1]
		bpy.data.objects['eyeL'].location[2] = (eyes_posL[0]) + eyeL_origin[2]

		bpy.data.objects['eyeR'].scale[0] = eyes_size[0]*1.2
		bpy.data.objects['eyeR'].scale[1] = eyes_size[1]*1.2
		bpy.data.objects['eyeR'].scale[2] = eyes_size[2]*1.2
		bpy.data.objects['eyeL'].scale[0] = eyes_size[0]*1.2
		bpy.data.objects['eyeL'].scale[1] = eyes_size[1]*1.2
		bpy.data.objects['eyeL'].scale[2] = eyes_size[2]*1.2
		pes_diff_bin_data.append(eyes_size[0])
		if os.path.isfile(oralpath):
			bpy.data.objects['mouth'].select = True
			bpy.ops.object.delete() 
	return 1


def pes_diff_bin_exp(pes_diff_fname):
	scn = bpy.context.scene
	header_data = open(pes_diff_fname, 'rb').read(4)
	header_string = str(header_data, "utf-8")
	if header_string == "FACE":

		if not os.path.isfile(oralpath): 
			m0 = (bpy.data.objects['mouth'].location[0] + mouth_origin[0])
			m2 = (bpy.data.objects['mouth'].location[1] +  mouth_origin[1])*-1
			m1 = (bpy.data.objects['mouth'].location[2] - mouth_origin[2])

		rx = (bpy.data.objects['eyeR'].location[0] + eyeR_origin[0])*-1
		ry = (bpy.data.objects['eyeR'].location[1] + eyeR_origin[1])
		rz = (bpy.data.objects['eyeR'].location[2] - eyeR_origin[2])
		
		lx = (bpy.data.objects['eyeL'].location[0] - eyeL_origin[0])*-1
		ly = (bpy.data.objects['eyeL'].location[1] + eyeL_origin[1])
		lz = (bpy.data.objects['eyeL'].location[2] - eyeL_origin[2])

		bpy.data.objects['eyeR'].scale[0] = scn.eyes_size*1.2
		bpy.data.objects['eyeR'].scale[1] = scn.eyes_size*1.2
		bpy.data.objects['eyeR'].scale[2] = scn.eyes_size*1.2
		bpy.data.objects['eyeL'].scale[0] = scn.eyes_size*1.2
		bpy.data.objects['eyeL'].scale[1] = scn.eyes_size*1.2
		bpy.data.objects['eyeL'].scale[2] = scn.eyes_size*1.2

		pes_diff_data = open(pes_diff_fname, 'r+b')
		#Writing eye size
		pes_diff_data.seek(0x08)
		pes_diff_data.write(struct.pack('3f', scn.eyes_size, scn.eyes_size, scn.eyes_size))
		#Writing mouth position
		if not os.path.isfile(oralpath):  # If oral.fmdl not available
		   pes_diff_data.seek(0x3c)
		   pes_diff_data.write(struct.pack('3f', m0, m1, m2))
		# Writing eye position
		pes_diff_data.seek(0x150)
		pes_diff_data.write(struct.pack('3f', rz, ry, rx))  # Write eye Right

		pes_diff_data.seek(0x160)
		pes_diff_data.write(struct.pack('3f', lz, ly, lx))  # Write eye Left
		pes_diff_data.flush()
		pes_diff_data.close()

	return 1

def texconv(inPath, outPath, arguments, cm):
	File = open(inPath, 'r', encoding="cp437")
	File.seek(0x54)
	TxFormat = File.read(4)
	File.close()
	if cm:
		if TxFormat == "DX10":
			args = arguments + ' "' + outPath + '" "' + inPath + '"'
			os.system('"' + texconvTools + args + '"')
	else:
		args = arguments + ' "' + outPath + '" "' + inPath + '"'
		os.system('"' + texconvTools + args + '"')
	return 1


def convert_ftex(ftexfilepath):
	ftexname = ' "' + ftexfilepath + '"'
	os.system('"' + FtexTools + ftexname + '"')
	return 1


def convert_dds(ftexfilepath):
	ftexname = ' -f 0 "' + ftexfilepath + '"'
	os.system('"' + FtexTools + ftexname + '"')

	return 1


def texture_covert(dirPath):
	for root, directories, filenames in os.walk(dirPath):
		for fileName in filenames:
			filename, extension = os.path.splitext(fileName)
			if extension.lower() == '.dds':
				ddsPath = os.path.join(root, filename + extension)
				texconv(ddsPath, root, " -r -y -f BC7_UNORM -dx10 -ft dds -o ", False)
				convert_dds(ddsPath)

	return root, directories, filenames

def texture_load(dirPath):
	for root, directories, filenames in os.walk(dirPath):
		for fileName in filenames:
			filename, extension = os.path.splitext(fileName)
			if extension.lower() == '.ftex':
				ddsPath = os.path.join(root, filename + '.dds')
				ftexPath = os.path.join(root, filename + extension)
				try:
					Ftex.ftexToDds(ftexPath, ddsPath)
				except:
					convert_ftex(ftexPath)
				texconv(ddsPath, dirPath, " -r -y -f DXT5 -ft dds -o ", True)
				
	return root, directories, filenames



def remove_dds(dirPath):
	for root, directories, filenames in os.walk(dirPath):
		for fileName in filenames:
			filename, extension = os.path.splitext(fileName)
			if extension.lower() == '.dds' or extension.lower() == '.png' or extension.lower() == '.tga':
				ddsPath = os.path.join(root, filename + extension)
				os.remove(ddsPath)
				print('Removing texture [>{0}{1}<] succesfully'.format(filename, extension))
	return root, directories, filenames

	
def materialname(meshname, matname):
	for slot in bpy.data.objects[meshname].material_slots:
		bpy.data.materials[slot.name].name = matname
	return 1


vertexGroupSummaryCache = {}


def defaultEnum(self):
	try:
		for ob in bpy.data.objects:
			if ob.type == 'MESH' and ob.data is not None:
				ob.select=True
				for slot in bpy.data.objects[ob.name].material_slots:
					materials_name = slot.name
					technique = bpy.data.materials[materials_name].fmdl_material_technique
					if technique  == 'pes3DDF_Skin_Face':
						bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 0
						bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 0
					elif technique  == 'pes3DDC_Wet':
						bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 0
						bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 81
					elif technique  == 'pes3DDC_Adjust_100':
						bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 0
						bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 80
					elif technique  == 'fox3DDC_Blin':
						bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 0
						bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 112
					elif technique  == 'pes3DFW_EyeOcclusion':
						bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 37
						bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 112
					#Same technique but different material and value.
					elif technique == 'pes3DDF_Hair2':
						if  materials_name.startswith('fox_hair_mat'):
							bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 0
							bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 160
						else:
							bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 1
							bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 160
					elif technique == 'pes3DDF_Hair2_NrmUV':
						if  materials_name.startswith('fox_hair_mat'):
							bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 0
							bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 160
						else:
							bpy.data.meshes[ob.data.name].fmdl_shadow_enum = 1
							bpy.data.meshes[ob.data.name].fmdl_alpha_enum = 160
			ob.select=False
		self.report({"INFO"}, "Enum has been reset to default!!")
	except Exception as exception:
		self.report({"WARNING"}, format(exception))
		print(format(type(exception).__name__), format(exception))
		return {'CANCELLED'}
	return 1


def importFmdlfile(fileName, sklname, meshID, objName):
	context = bpy.context


	extensions_enabled = context.scene.fmdl_import_extensions_enabled

	loop_preservation = context.scene.fmdl_import_loop_preservation
	mesh_splitting = context.scene.fmdl_import_mesh_splitting
	load_textures = context.scene.fmdl_import_load_textures
	import_all_bounding_boxes = context.scene.fmdl_import_all_bounding_boxes
	fixmeshesmooth = context.scene.fixmeshesmooth

	importSettings = IO.ImportSettings()
	importSettings.enableExtensions = extensions_enabled
	importSettings.enableVertexLoopPreservation = loop_preservation
	importSettings.enableMeshSplitting = mesh_splitting
	importSettings.enableLoadTextures = load_textures
	importSettings.enableImportAllBoundingBoxes = import_all_bounding_boxes
	importSettings.fixMeshsmooth = fixmeshesmooth
	importSettings.armatureName = sklname
	importSettings.meshIdName = meshID

	fmdlFile = FmdlFile.FmdlFile()
	fmdlFile.readFile(fileName)

	rootObject = IO.importFmdl(context, fmdlFile, objName, importSettings)
	rootObject.fmdl_export_extensions_enabled = importSettings.enableExtensions
	rootObject.fmdl_export_loop_preservation = importSettings.enableVertexLoopPreservation
	rootObject.fmdl_export_mesh_splitting = importSettings.enableMeshSplitting


	return 1

def exportFmdlfile(fileName, meshID, objName):
	context = bpy.context

	for ob in bpy.data.objects:
		if context.scene.objects.active == None:
			object = bpy.data.objects[ob.name]
			bpy.context.scene.objects.active = object

	extensions_enabled = context.active_object.fmdl_export_extensions_enabled
	loop_preservation = context.active_object.fmdl_export_loop_preservation
	mesh_splitting = context.active_object.fmdl_export_mesh_splitting

	exportSettings = IO.ExportSettings()
	exportSettings.enableExtensions = extensions_enabled
	exportSettings.enableVertexLoopPreservation = loop_preservation
	exportSettings.enableMeshSplitting = mesh_splitting
	exportSettings.meshIdName = meshID
	try:
		fmdlFile = IO.exportFmdl(context, objName, exportSettings)
	except IO.FmdlExportError as error:
		print("Error exporting Fmdl:\n" + "\n".join(error.errors))
		return {'CANCELLED'}
	fmdlFile.writeFile(fileName)
	return 1

def is_number(n):
    is_number = True
    try:
        num = complex(n)
        is_number = num == num
    except ValueError:
        is_number = False
    return is_number

def oldIDread():
	scn = bpy.context.scene
	old_path = scn.face_path[:-29]
	IDFinds = str()
	oldID = str()
	try:
		for i in range(100):
			IDFinds = re.findall(r'\w+', old_path)
			oldID= IDFinds[i]
	except:
		pass

	try:
		scn.oldid = oldID
	except:
		scn.idread = False
	pass

def NewID():

	scn = bpy.context.scene
	OLD_ID = scn.oldid
	NEW_ID = scn.newid
	facepath = scn.face_path
	old_path = facepath[:-29]
	new_path = facepath[:-29]
	scene_new_path = facepath
	IDFinds = str()
	OLD_ID2 = str()
	for ob in bpy.data.objects:
		for mat_slot in ob.material_slots:
			for mtex_slot in mat_slot.material.texture_slots:
				if mtex_slot is not None:
					if '_Tex_' in mtex_slot.name:	
						texname = bpy.data.textures[mtex_slot.name].fmdl_texture_directory
						if 'real' in texname:
							IDFinds = re.findall(r'\w+', old_path)
							texname = texname.replace(texname, "/Assets/pes16/model/character/face/real/%s/sourceimages/" % NEW_ID)
							bpy.data.textures[mtex_slot.name].fmdl_texture_directory = texname
	for i in range(100):
		if len(IDFinds) == i+1:
			OLD_ID2 = IDFinds[i]
	if is_number(OLD_ID):
		scene_new_path = scene_new_path.replace(OLD_ID2, NEW_ID)
		new_path = new_path.replace(OLD_ID2, NEW_ID)
		os.rename(old_path, new_path)
		scn.face_path = scene_new_path
	pass

def vertexGroupSummaryGet(objectName):
	global vertexGroupSummaryCache
	if objectName not in vertexGroupSummaryCache:
		return None
	return vertexGroupSummaryCache[objectName]


def vertexGroupSummarySet(objectName, value):
	global vertexGroupSummaryCache
	vertexGroupSummaryCache[objectName] = value


def vertexGroupSummaryRemove(objectName):
	global vertexGroupSummaryCache
	if objectName in vertexGroupSummaryCache:
		del vertexGroupSummaryCache[objectName]


def vertexGroupSummaryCleanup(objectNames):
	global vertexGroupSummaryCache
	for objectName in list(vertexGroupSummaryCache.keys()):
		if objectName not in objectNames:
			del vertexGroupSummaryCache[objectName]

def exportSummaryTextName(objectName):
	return "Export Summary for %s" % objectName

class FMDL_Scene_Extract_Fpk(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
	"""Load a PES FPK file"""
	bl_idname = "extract_scene.fpk"
	bl_label = "Extract Face.Fpk"
	bl_options = {'REGISTER', 'UNDO'}

	face_high_fmdl = bpy.props.BoolProperty(name = "Import face_high.fmdl", default = True)
	hair_high_fmdl = bpy.props.BoolProperty(name = "Import hair_high.fmdl", default = True)
	oral_fmdl = bpy.props.BoolProperty(name = "Import oral.fmdl", default = True)
	pes_diff_bin = bpy.props.BoolProperty(name = "Import face_diff.bin", default = True)
	fixMeshsmooth = bpy.props.BoolProperty(name = "FIX-Smooth Meshes", default = True)
	
	import_label = "PES FPK (.fpk)"
	
	filename_ext = ""
	filter_glob = bpy.props.StringProperty(default="face.fpk", options={'HIDDEN'})

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	config.read(ini_sett)
	def invoke(self, context, event):
		if context.scene.face_cnf == False:
			self.report({"WARNING"}, "Face ID has change you need to export!")
			return {'CANCELLED'}
		if context.scene.hair_cnf == False:
			self.report({"WARNING"}, "Hair ID has change you need to export!")
			return {'CANCELLED'}
		if context.scene.fpk_cnf == False:
			self.report({"WARNING"}, "ID has change you need to create .fpk!")
			return {'CANCELLED'}

		self.face_high_fmdl = context.scene.import_face_high
		self.hair_high_fmdl = context.scene.import_hair_high
		self.oral_fmdl = context.scene.import_oral
		self.pes_diff_bin = context.scene.import_pes_diff
		self.fixMeshsmooth = context.scene.fixmeshesmooth

		self.face_high_fmdl = config.get('bl_sett', 'face_high').lower() in 'true'
		self.hair_high_fmdl = config.get('bl_sett', 'hair_high').lower() in 'true'
		self.oral_fmdl = config.get('bl_sett', 'oral').lower() in 'true'
		self.pes_diff_bin = config.get('bl_sett', 'pes_diff').lower() in 'true'

		return bpy_extras.io_utils.ImportHelper.invoke(self, context, event)

	def execute(self, context):

		context.scene.fixmeshesmooth = self.fixMeshsmooth
		config.set('bl_sett', 'face_high', str(self.face_high_fmdl))
		config.set('bl_sett', 'hair_high', str(self.hair_high_fmdl))
		config.set('bl_sett', 'oral', str(self.oral_fmdl))
		config.set('bl_sett', 'pes_diff', str(self.pes_diff_bin))
		with open(ini_sett, 'w') as f:
			config.write(f)
		filename = self.filepath
		face_path = filename[:-4] + "_fpk\\face_high.fmdl"
		context.scene.face_path = face_path
		fpk = ' "' + filename + '"'
		os.system('"' + GZSPATH + fpk + '"')
		facepath = context.scene.face_path
		hairpath = facepath[:-14] + "hair_high.fmdl"
		oralpath = facepath[:-14] + "oral.fmdl"
		pes_diff_fname = facepath[:-14] + "face_diff.bin"
		dirpath = facepath[:-29] + "\\sourceimages\\#windx11"
		if context.scene.fmdl_import_load_textures:
			texture_load(dirpath)
		if self.face_high_fmdl:
			if not "face_high" in bpy.data.objects:
				pes_diff_bin_data.clear()
				importFmdlfile(facepath, "Skeleton_Face", "mesh_id_face", "face_high")

				self.report({"INFO"}, "Face Imported Succesfully")
				oldIDread()
				if context.scene.idread == False:
					print("Can't read Old ID, you can't Relink ID rightnow!")
				print("Face Imported Succesfully")
			else:
				self.report({"WARNING"}, "Face Already Imported!!")
		if self.hair_high_fmdl:
			if not "hair_high" in bpy.data.objects:
				pes_diff_bin_data.clear()
				fileName = hairpath
				importFmdlfile(fileName, "Skeleton_Hair", "mesh_id_hair", "hair_high")
				oldIDread()
				print("Hair Inported Succesfully")
				if context.scene.idread == False:
					print("Can't read Old ID, you can't Relink ID rightnow!")
			else:
				self.report({"WARNING"}, "Hair Already Imported!!")
		if self.oral_fmdl:
			if not "oral_high" in bpy.data.objects:
				fileName = oralpath
				if os.path.isfile(fileName):
					pes_diff_bin_data.clear()
					importFmdlfile(fileName, "Skeleton_Oral", "mesh_id_oral", "oral_high")
					print("Oral Inported Succesfully")
			else:
				self.report({"WARNING"}, "Oral Already Imported!!")
		if self.pes_diff_bin:
			pes_diff_bin_imp(pes_diff_fname)
			print("pes_diff.bin imported succesfully!")
		self.report({"INFO"}, "Extract Face.fpk succesfully!")
		return {'FINISHED'}


class FMDL_Scene_Open_Image(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
	"""Open a Image Texture FTEX or DDS"""
	bl_idname = "open.image"
	bl_label = "Open Image Texture"
	bl_options = {'REGISTER', 'UNDO'}

	
	import_label = "Open Image Texture"
	
	filename_ext = "DDS, FTEX, PNG, TGA"
	filter_glob = bpy.props.StringProperty(default="*.dds;*.ftex;*.png;*.tga", options={'HIDDEN'})

	
	def execute(self, context):

		filePath = self.filepath
		fileName = str(filePath).split('..')[0].split('\\')[-1:][0]
		dirpath = os.path.dirname(filePath)

		filenames, extension = os.path.splitext(fileName)
		if extension.lower() == '.ftex':
			fileName = filenames + '.dds'
			DDSPath = os.path.join(dirpath, fileName)
			try:
				Ftex.ftexToDds(filePath, DDSPath)
			except:
				convert_ftex(filePath)
			texconv(DDSPath, dirpath, " -r -y -f DXT5 -ft dds -o ", True)
			filePath = DDSPath
		elif extension.lower() == '.png':
			fileName = filenames + extension
			PNGPath = os.path.join(dirpath, fileName)
			texconv(PNGPath, dirpath, " -r -y -l -f DXT5 -ft dds -srgb -o ", False)
			fileName = filenames + '.dds'
			PNGPath = os.path.join(dirpath, fileName)
			filePath = PNGPath
		elif extension.lower() == '.tga':
			fileName = filenames + extension
			TGAPath = os.path.join(dirpath, fileName)
			texconv(TGAPath, dirpath, " -r -y -l -f DXT5 -ft dds -srgb -o ", False)
			fileName = filenames + '.dds'
			TGAPath = os.path.join(dirpath, fileName)
			filePath = TGAPath
		if fileName in bpy.data.images:
			image = bpy.data.images[fileName]
		else:
			image = bpy.data.images.new(name=fileName, width=1024, height=1024, alpha=True,float_buffer=False)
		image.source = 'FILE'
		image.filepath=filePath

		mesh=context.scene.objects.active.data
		uvdata = str()

		texName=context.active_object.active_material.active_texture.name
		texture_role = bpy.data.textures[texName].fmdl_texture_role
		idx = context.object.active_material.active_texture_index
		
		if texture_role == str():
			self.report({"WARNING"}, "Need set shader first!!")
			return {'CANCELLED'}
		
		if mesh.uv_textures.active_index == -1:
			self.report({"WARNING"}, "Need create UVMap first!!")
			return {'CANCELLED'}

		if mesh.uv_textures.active_index == idx:
			uvdata = mesh.uv_textures[idx].data

		context.active_object.active_material.active_texture.name = "[%s] %s" % (texture_role, fileName)
		texname=context.active_object.active_material.active_texture.name
		bpy.data.textures[texname].fmdl_texture_filename = fileName

		for face in uvdata:
			face.image=image
			image.reload()

		imageTexture = bpy.data.textures[texname]
		imageTexture.image = image
		imageTexture.use_alpha = True


		if '_SRGB' in texture_role:
			image.colorspace_settings.name = 'sRGB'
		elif '_LIN' in texture_role:
			image.colorspace_settings.name = 'Linear'
		else:
			image.colorspace_settings.name = 'Non-Color'

		if '_NRM' in texture_role:
			imageTexture.use_normal_map = True

		self.report({"INFO"}, "Add texture [%s] succesfully!" % fileName)
		return {'FINISHED'}
		

def updateSummaries(scene):
	textNames = set()
	for object in scene.objects:
		objectName = object.name
		parent = object.parent
		while parent is not None:
			objectName = "%s/%s" % (parent.name, objectName)
			parent = parent.parent

		textName = exportSummaryTextName(objectName)
		if object.fmdl_file:
			textNames.add(textName)
			summary = IO.exportSummary(bpy.context, object.name)
			if textName in bpy.data.texts:
				text = bpy.data.texts[textName]
				if text.as_string() != summary:
					text.from_string(summary)
			else:
				text = bpy.data.texts.new(textName)
				text.user_clear()  # blender bug: texts start as users=1 instead of users=0
				text.from_string(summary)
				c = bpy.context.copy()
				c['edit_text'] = text
				bpy.ops.text.make_internal(c)
				bpy.ops.text.jump(c, line=1)
	removeList = []
	for textName in bpy.data.texts.keys():
		if textName.startswith("Export Summary for ") and textName not in textNames:
			removeList.append(textName)
	for textName in removeList:
		bpy.data.texts.remove(bpy.data.texts[textName])


latestObjectTree = ()


@bpy.app.handlers.persistent
def FMDL_Scene_TrackExportSummaryUpdates(scene):
	if bpy.context.mode != 'OBJECT':
		return
	found = scene.is_updated or scene.is_updated_data
	if not found:
		objectTree = []
		for object in scene.objects:
			objectTree.append((object.name, object.parent.name if object.parent is not None else None))
			if object.is_updated or object.is_updated_data:
				found = True
		objectTuple = tuple(objectTree)
		global latestObjectTree
		if objectTuple != latestObjectTree:
			latestObjectTree = objectTuple
			found = True
	if found:
		updateSummaries(scene)


class FMDL_Util_window_set_screen(bpy.types.Operator):
	"""Set window screen"""
	bl_idname = "fmdl.window_set_screen"
	bl_label = "Set window screen"
	bl_options = {'INTERNAL'}

	screenName = bpy.props.StringProperty(name="Screen name")

	def execute(self, context):
		context.window.screen = bpy.data.screens[self.screenName]
		return {'FINISHED'}


def createTextEditWindow(context):
	originalWindow = context.window

	bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
	screen = context.window_manager.windows[-1].screen

	# This must happen before the window is destroyed.
	screen.areas[0].type = 'TEXT_EDITOR'

	screen.name = "Export Summaries"
	screenName = screen.name
	c = context.copy()
	c['window'] = context.window_manager.windows[-1]
	bpy.ops.wm.window_close(c)

	c = context.copy()
	c['window'] = originalWindow
	bpy.ops.wm.window_duplicate(c)
	oldScreenName = context.window_manager.windows[-1].screen.name

	c = context.copy()
	c['window'] = context.window_manager.windows[-1]
	c['screen'] = bpy.data.screens[oldScreenName]
	bpy.ops.screen.delete(c)

	c = context.copy()
	c['window'] = context.window_manager.windows[-1]
	bpy.ops.fmdl.window_set_screen(c, screenName=screen.name)

	return screen.areas[0]


def createTextEditArea(context):
	for window in context.window_manager.windows:
		if window.screen is not None:
			for area in window.screen.areas:
				if area.type == 'TEXT_EDITOR':
					return area
	return createTextEditWindow(context)



class FMDL_Scene_Panel_FMDL_Import_Settings(bpy.types.Menu):
	"""Import Settings"""
	bl_label = "Import settings"

	def draw(self, context):
		self.layout.prop(context.scene, 'fmdl_import_extensions_enabled')

		row = self.layout.row()
		row.prop(context.scene, 'fmdl_import_loop_preservation')
		row.enabled = context.scene.fmdl_import_extensions_enabled

		row = self.layout.row()
		row.prop(context.scene, 'fmdl_import_mesh_splitting')
		row.enabled = context.scene.fmdl_import_extensions_enabled

		row = self.layout.row()
		row.prop(context.scene, 'fmdl_import_load_textures')

		row = self.layout.row()
		row.prop(context.scene, 'fmdl_import_all_bounding_boxes')

		row = self.layout.row()
		row.prop(context.scene, 'fixmeshesmooth')


class FMDL_Scene_Panel_FMDL_Export_Settings(bpy.types.Menu):
	"""Export Settings"""
	bl_label = "Export settings"

	def draw(self, context):
		if context.active_object is not None:
			self.layout.prop(context.active_object, 'fmdl_export_extensions_enabled')
			row = self.layout.row()
			row.prop(context.active_object, 'fmdl_export_loop_preservation')
			row.enabled = context.active_object.fmdl_export_extensions_enabled
			row = self.layout.row()
			row.prop(context.active_object, 'fmdl_export_mesh_splitting')
			row.enabled = context.active_object.fmdl_export_extensions_enabled


class FMDL_Object_BoundingBox_Create(bpy.types.Operator):
	"""Create custom bounding box"""
	bl_idname = "fmdl.boundingbox_create"
	bl_label = "Create custom bounding box"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if not (
				context.mode == 'OBJECT'
				and context.object is not None
				and context.object.type == 'MESH'
		):
			return False
		for child in context.object.children:
			if child.type == 'LATTICE':
				return False
		return True

	def execute(self, context):
		IO.createFittingBoundingBox(context, context.object)
		return {'FINISHED'}


class FMDL_Object_BoundingBox_Remove(bpy.types.Operator):
	"""Remove custom bounding box"""
	bl_idname = "fmdl.boundingbox_remove"
	bl_label = "Remove custom bounding box"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if not (
				context.mode == 'OBJECT'
				and context.object is not None
				and context.object.type == 'MESH'
		):
			return False
		for child in context.object.children:
			if child.type == 'LATTICE':
				return True
		return False

	def execute(self, context):
		removeList = []
		for child in context.object.children:
			if child.type == 'LATTICE':
				removeList.append(child.name)
		for objectID in removeList:
			latticeID = bpy.data.objects[objectID].data.name
			while len(bpy.data.objects[objectID].users_scene) > 0:
				bpy.data.objects[objectID].users_scene[0].objects.unlink(bpy.data.objects[objectID])
			if bpy.data.objects[objectID].users == 0:
				bpy.data.objects.remove(bpy.data.objects[objectID])
			if bpy.data.lattices[latticeID].users == 0:
				bpy.data.lattices.remove(bpy.data.lattices[latticeID])
		return {'FINISHED'}


class FMDL_Object_BoundingBox_Panel(bpy.types.Panel):
	bl_label = "FMDL Bounding Box"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (
				context.object is not None
				and context.object.type == 'MESH'
		)

	def draw(self, context):
		self.layout.operator(FMDL_Object_BoundingBox_Create.bl_idname)
		self.layout.operator(FMDL_Object_BoundingBox_Remove.bl_idname)


@bpy.app.handlers.persistent
def FMDL_Mesh_BoneGroup_TrackVertexGroupUsageUpdates(scene):
	if bpy.context.mode != 'OBJECT':
		return
	meshObjectNames = set()
	for object in scene.objects:
		if object.type == 'MESH':
			if object.is_updated_data:
				vertexGroupSummaryRemove(object.name)
			else:
				meshObjectNames.add(object.name)
	vertexGroupSummaryCleanup(meshObjectNames)


def FMDL_Mesh_BoneGroup_Bone_get_enabled(bone):
	return bone.name in bpy.context.active_object.vertex_groups


def FMDL_Mesh_BoneGroup_Bone_set_enabled(bone, enabled):
	vertex_groups = bpy.context.active_object.vertex_groups
	if enabled and bone.name not in vertex_groups:
		vertex_groups.new(bone.name)
		vertexGroupSummaryRemove(bpy.context.active_object.name)
	if not enabled and bone.name in vertex_groups:
		vertex_groups.remove(vertex_groups[bone.name])
		vertexGroupSummaryRemove(bpy.context.active_object.name)


class VertexGroupUsageSummary:
	def __init__(self):
		self.vertices = {}
		self.totalWeights = {}

	@staticmethod
	def meshObjectActiveArmature(meshObject):
		activeArmature = None
		for modifier in meshObject.modifiers:
			if modifier.type == 'ARMATURE':
				if activeArmature != None:
					return None
				activeArmature = modifier.object.data
		return activeArmature

	@staticmethod
	def compute(meshObject, armature):
		if vertexGroupSummaryGet(meshObject.name) != None:
			return
		summary = VertexGroupUsageSummary()
		for bone in armature.bones:
			summary.vertices[bone.name] = 0
			summary.totalWeights[bone.name] = 0.0
		vertexGroupNames = {}
		for vertexGroup in meshObject.vertex_groups:
			vertexGroupNames[vertexGroup.index] = vertexGroup.name
		for vertex in meshObject.data.vertices:
			for groupElement in vertex.groups:
				if groupElement.group not in vertexGroupNames:
					continue
				groupName = vertexGroupNames[groupElement.group]
				if groupName not in summary.vertices:
					continue
				summary.vertices[groupName] += 1
				summary.totalWeights[groupName] += groupElement.weight
		vertexGroupSummarySet(meshObject.name, summary)


class FMDL_Mesh_BoneGroup_List(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		armature = data
		meshObject = active_data

		row = layout.row(align=True)
		if meshObject.mode == 'OBJECT' and meshObject.data.fmdl_show_vertex_group_details:
			vertexGroupSummary = vertexGroupSummaryGet(meshObject.name)
			vertexCount = vertexGroupSummary.vertices[item.name]
			totalWeight = vertexGroupSummary.totalWeights[item.name]

			if meshObject.data.fmdl_show_vertex_group_vertices and meshObject.data.fmdl_show_vertex_group_weights:
				mainRow = row.split(percentage=0.55, align=True)
			elif meshObject.data.fmdl_show_vertex_group_vertices or meshObject.data.fmdl_show_vertex_group_weights:
				mainRow = row.split(percentage=0.7, align=True)
			else:
				mainRow = row.split(percentage=1.0, align=True)

			checkboxNameRow = mainRow.row(align=True)
			checkboxRow = checkboxNameRow.row()
			checkboxRow.enabled = (not meshObject.data.fmdl_lock_nonempty_vertex_groups or vertexCount == 0)
			checkboxRow.prop(item, 'fmdl_bone_in_active_mesh', text='')
			checkboxNameRow.label(text=item.name)

			if meshObject.data.fmdl_show_vertex_group_vertices and meshObject.data.fmdl_show_vertex_group_weights:
				verticesRow = mainRow.split(percentage=0.45, align=True)
				verticesRow.alignment = 'RIGHT'
			elif meshObject.data.fmdl_show_vertex_group_vertices or meshObject.data.fmdl_show_vertex_group_weights:
				verticesRow = mainRow.split(percentage=1.0, align=True)
				verticesRow.alignment = 'RIGHT'

			if meshObject.data.fmdl_show_vertex_group_vertices:
				verticesRow.label("%d v" % vertexCount)
			if meshObject.data.fmdl_show_vertex_group_weights:
				verticesRow.label("%.1f w" % totalWeight)
		else:
			row.prop(item, 'fmdl_bone_in_active_mesh', text='')
			row.label(text=item.name)

	def filter_items(self, context, data, propname):
		boneNames = [bone.name for bone in data.bones]
		indices = {}
		for name in sorted(boneNames):
			indices[name] = len(indices)
		order = [indices[name] for name in boneNames]
		return ([], order)


class FMDL_Mesh_BoneGroup_RemoveUnused(bpy.types.Operator):
	"""Remove bones not bound to any vertices"""
	bl_idname = "fmdl.bonegroup_remove_unused"
	bl_label = "Remove Unused"
	bl_options = {'UNDO'}

	@classmethod
	def poll(cls, context):
		return (
				context.active_object != None
				and context.active_object.type == 'MESH'
				and context.active_object.mode == 'OBJECT'
				and VertexGroupUsageSummary.meshObjectActiveArmature(context.active_object) != None
		)

	def execute(self, context):
		armature = VertexGroupUsageSummary.meshObjectActiveArmature(context.active_object)
		VertexGroupUsageSummary.compute(context.active_object, armature)
		vertexGroupSummary = vertexGroupSummaryGet(context.active_object.name)
		for (boneName, vertexCount) in vertexGroupSummary.vertices.items():
			if vertexCount == 0 and boneName in context.active_object.vertex_groups:
				context.active_object.vertex_groups.remove(context.active_object.vertex_groups[boneName])
		vertexGroupSummaryRemove(context.active_object.name)
		return {'FINISHED'}


class FMDL_Mesh_BoneGroup_Refresh(bpy.types.Operator):
	"""Refresh bone usage details"""
	bl_idname = "fmdl.bonegroup_refresh"
	bl_label = "Refresh"
	bl_options = set()

	@classmethod
	def poll(cls, context):
		return (
				context.active_object != None
				and context.active_object.type == 'MESH'
				and context.active_object.mode == 'OBJECT'
		)

	def execute(self, context):
		vertexGroupSummaryRemove(context.active_object.name)
		return {'FINISHED'}


class FMDL_Mesh_BoneGroup_CopyFromSelected(bpy.types.Operator):
	"""Copy bone group from selected mesh"""
	bl_idname = "fmdl.bonegroup_copy_from_selected"
	bl_label = "Copy Bone Group from Selected"
	bl_options = {'UNDO'}

	@staticmethod
	def selectedObject(context, requiredType):
		differentObject = None
		for object in context.selected_objects:
			if object.name != context.active_object.name and object.type == requiredType:
				if differentObject != None:
					return None
				differentObject = object
		return differentObject

	@classmethod
	def poll(cls, context):
		return (
				context.active_object != None
				and context.active_object.type == 'MESH'
				and context.active_object.mode == 'OBJECT'
				and VertexGroupUsageSummary.meshObjectActiveArmature(context.active_object) != None
				and FMDL_Mesh_BoneGroup_CopyFromSelected.selectedObject(context, 'MESH') != None
		)

	def execute(self, context):
		selectedMeshObject = FMDL_Mesh_BoneGroup_CopyFromSelected.selectedObject(context, 'MESH')
		desiredBones = selectedMeshObject.vertex_groups.keys()
		armature = VertexGroupUsageSummary.meshObjectActiveArmature(context.active_object)
		VertexGroupUsageSummary.compute(context.active_object, armature)
		vertexGroupSummary = vertexGroupSummaryGet(context.active_object.name)
		for boneName in context.active_object.vertex_groups.keys():
			if (
					boneName in vertexGroupSummary.vertices
					and vertexGroupSummary.vertices[boneName] == 0
					and boneName not in desiredBones
			):
				context.active_object.vertex_groups.remove(context.active_object.vertex_groups[boneName])
		for boneName in desiredBones:
			if (
					boneName not in context.active_object.vertex_groups
					and boneName in armature.bones
			):
				context.active_object.vertex_groups.new(boneName)
		vertexGroupSummaryRemove(context.active_object.name)
		return {'FINISHED'}


class FMDL_Mesh_BoneGroup_Specials(bpy.types.Menu):
	bl_label = "Bone Group operations"

	def draw(self, context):
		self.layout.operator(FMDL_Mesh_BoneGroup_RemoveUnused.bl_idname, icon='X')
		self.layout.operator(FMDL_Mesh_BoneGroup_Refresh.bl_idname, icon='FILE_REFRESH')
		self.layout.operator(FMDL_Mesh_BoneGroup_CopyFromSelected.bl_idname, icon='LINK_AREA')


class FMDL_Mesh_BoneGroup_Panel(bpy.types.Panel):
	bl_label = "FMDL Bone Group"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return (
				context.mesh != None
				and context.object != None
				and VertexGroupUsageSummary.meshObjectActiveArmature(context.object) != None
		)

	def draw(self, context):
		meshObject = context.object
		mesh = meshObject.data
		armature = VertexGroupUsageSummary.meshObjectActiveArmature(meshObject)

		computeDetails = (meshObject.mode == 'OBJECT' and mesh.fmdl_show_vertex_group_details)
		if computeDetails:
			VertexGroupUsageSummary.compute(meshObject, armature)

		self.layout.template_list(
			FMDL_Mesh_BoneGroup_List.__name__,
			"FMDL_Mesh_BoneGroups",
			armature,
			"bones",
			meshObject,
			"fmdl_bone_active",
			rows=8
		)

		groupSize = len(meshObject.vertex_groups)

		summaryRow = self.layout.row()
		summaryRow.label("Bone group size: %s/32%s" % (groupSize, ' (!!)' if groupSize > 32 else ''))
		summaryRow.menu(FMDL_Mesh_BoneGroup_Specials.__name__, icon='DOWNARROW_HLT', text="")

		detailLayout = self.layout.row()
		detailLayoutSplit = detailLayout.split(percentage=0.6)
		leftColumn = detailLayoutSplit.column()
		rightColumn = detailLayoutSplit.column()

		detailRow = leftColumn.row()
		detailRow.enabled = (meshObject.mode == 'OBJECT')
		detailRow.prop(mesh, 'fmdl_show_vertex_group_details')
		lockRow = leftColumn.row()
		lockRow.enabled = computeDetails
		lockRow.prop(mesh, 'fmdl_lock_nonempty_vertex_groups')

		verticesRow = rightColumn.row()
		verticesRow.enabled = computeDetails
		verticesRow.prop(mesh, 'fmdl_show_vertex_group_vertices')
		weightsRow = rightColumn.row()
		weightsRow.enabled = computeDetails
		weightsRow.prop(mesh, 'fmdl_show_vertex_group_weights')


class FMDL_Mesh_Panel(bpy.types.Panel):
	bl_label = "FMDL Mesh Settings"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return context.mesh != None

	def draw(self, context):
		mesh = context.mesh
		mainColumn = self.layout.column()
		mainColumn.operator("primary.operator", text="Set to Default Enum", icon="LOAD_FACTORY").face_opname = "set_default_enum"
		mainColumn.prop(mesh, "fmdl_alpha_enum_select", text='Alpha')
		mainColumn.prop(mesh, "fmdl_shadow_enum_select", text='Shadow')
		mainColumn.prop(mesh, "fmdl_alpha_enum")
		mainColumn.prop(mesh, "fmdl_shadow_enum")


class FMDL_Material_Parameter_List_Add(bpy.types.Operator):
	bl_idname = "fmdl.material_parameter_add"
	bl_label = "Add Parameter"

	@classmethod
	def poll(cls, context):
		return context.material != None

	def execute(self, context):
		material = context.material
		parameter = material.fmdl_material_parameters.add()
		parameter.name = "new_parameter"
		parameter.parameters = [0.0, 0.0, 0.0, 0.0]
		material.fmdl_material_parameter_active = len(material.fmdl_material_parameters) - 1
		return {'FINISHED'}


class FMDL_Material_Parameter_List_Remove(bpy.types.Operator):
	bl_idname = "fmdl.material_parameter_remove"
	bl_label = "Remove Parameter"

	@classmethod
	def poll(cls, context):
		return (context.material != None and
				0 <= context.material.fmdl_material_parameter_active < len(context.material.fmdl_material_parameters)
				)

	def execute(self, context):
		material = context.material
		material.fmdl_material_parameters.remove(material.fmdl_material_parameter_active)
		if material.fmdl_material_parameter_active >= len(material.fmdl_material_parameters):
			material.fmdl_material_parameter_active = len(material.fmdl_material_parameters) - 1
		return {'FINISHED'}


class FMDL_Material_Parameter_List_MoveUp(bpy.types.Operator):
	bl_idname = "fmdl.material_parameter_moveup"
	bl_label = "Move Parameter Up"

	@classmethod
	def poll(cls, context):
		return (context.material != None and
				1 <= context.material.fmdl_material_parameter_active < len(context.material.fmdl_material_parameters)
				)

	def execute(self, context):
		material = context.material
		material.fmdl_material_parameters.move(
			material.fmdl_material_parameter_active,
			material.fmdl_material_parameter_active - 1
		)
		material.fmdl_material_parameter_active -= 1
		return {'FINISHED'}


class FMDL_Material_Parameter_List_MoveDown(bpy.types.Operator):
	bl_idname = "fmdl.material_parameter_movedown"
	bl_label = "Move Parameter Down"

	@classmethod
	def poll(cls, context):
		return (context.material != None and
				0 <= context.material.fmdl_material_parameter_active < len(
					context.material.fmdl_material_parameters) - 1
				)

	def execute(self, context):
		material = context.material
		material.fmdl_material_parameters.move(
			material.fmdl_material_parameter_active,
			material.fmdl_material_parameter_active + 1
		)
		material.fmdl_material_parameter_active += 1
		return {'FINISHED'}


class FMDL_Material_Parameter_Name_List(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		row = layout.row(align=True)
		row.alignment = 'EXPAND'
		row.prop(item, 'name', text="", emboss=False)

def update_shader_list(self, context):
	try:
		self.fox_shader = self.fmdl_material_shader
	except:
		pass

def update_alpha_list(self, context):
	try:
		self.fmdl_alpha_enum = int(self.fmdl_alpha_enum_select)
	except:
		pass

def update_alpha_enum(self, context):
	try:
		self.fmdl_alpha_enum_select = str(self.fmdl_alpha_enum)
	except:
		if not self.fmdl_alpha_enum_select == str(self.fmdl_alpha_enum):
			self.fmdl_alpha_enum_select = 'Unknown'
		pass

def update_shadow_list(self, context):
	try:
		self.fmdl_shadow_enum = int(self.fmdl_shadow_enum_select)
	except:
		pass

def update_shadow_enum(self, context):
	try:
		self.fmdl_shadow_enum_select = str(self.fmdl_shadow_enum)
	except:
		if not self.fmdl_shadow_enum_select == str(self.fmdl_shadow_enum):
			self.fmdl_shadow_enum_select = 'Unknown'
		pass

def update_eye_size(self, context):
	if len(pes_diff_bin_data) != 0:
		try:
			bpy.data.objects['eyeR'].scale[0] = self.eyes_size*1.2
			bpy.data.objects['eyeR'].scale[1] = self.eyes_size*1.2
			bpy.data.objects['eyeR'].scale[2] = self.eyes_size*1.2
			bpy.data.objects['eyeL'].scale[0] = self.eyes_size*1.2
			bpy.data.objects['eyeL'].scale[1] = self.eyes_size*1.2
			bpy.data.objects['eyeL'].scale[2] = self.eyes_size*1.2
		except:
			pass


class FMDL_Material_Panel(bpy.types.Panel):
	bl_label = "FMDL Material Settings"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "material"

	@classmethod
	def poll(cls, context):
		return context.material != None

	def draw(self, context):
		material = context.material
		layout = self.layout
		mainColumn = layout.column(align=True)
		box = layout.box()
		mainColumn = box.row(align=0)
		mainColumn.prop(material, "fox_shader", text="PES Fox Shader")
		mainColumn.operator("shader.operator", text="", icon="SEQ_SEQUENCER")
		mainColumn = box.row(align=0)
		mainColumn.prop(material, "fmdl_material_shader")
		mainColumn = box.row(align=0)
		mainColumn.prop(material, "fmdl_material_technique")
		mainColumn = box.row(align=0)
		mainColumn.separator()
		mainColumn.label("Material Parameters")
		mainColumn = box.row(align=0)
		parameterListRow = mainColumn.row()
		parameterListRow.template_list(
			FMDL_Material_Parameter_Name_List.__name__,
			"FMDL_Material_Parameter_Names",
			material,
			"fmdl_material_parameters",
			material,
			"fmdl_material_parameter_active"
		)

		listButtonColumn = parameterListRow.column(align=True)
		listButtonColumn.operator("fmdl.material_parameter_add", icon='ZOOMIN', text="")
		listButtonColumn.operator("fmdl.material_parameter_remove", icon='ZOOMOUT', text="")
		listButtonColumn.separator()
		listButtonColumn.operator("fmdl.material_parameter_moveup", icon='TRIA_UP', text="")
		listButtonColumn.operator("fmdl.material_parameter_movedown", icon='TRIA_DOWN', text="")
		mainColumn = box.row(align=0)
		if 0 <= material.fmdl_material_parameter_active < len(material.fmdl_material_parameters):
			valuesColumn = mainColumn.column()
			parameter = material.fmdl_material_parameter_active
			valuesColumn.prop(
				material.fmdl_material_parameters[parameter],
				"parameters"
			)


class FMDL_Texture_Load_Ftex(bpy.types.Operator):
	"""Load the FTEX texture"""
	bl_idname = "fmdl.load_ftex"
	bl_label = "Load FTEX texture"

	@classmethod
	def poll(cls, context):
		texture = context.texture
		return (
				texture != None and
				texture.type == 'IMAGE' and
				texture.image != None and
				texture.image.filepath.lower().endswith('.ftex')
		)
	def draw(self, context):
		texture = context.texture

		mainColumn = self.layout.column()
		mainColumn.prop(texture, "open_image", text="Texture Path")

	def execute(self, context):
		# Avoids a blender bug in which an invalid image can't be replaced with a valid one
		context.texture.image_user.use_auto_refresh = context.texture.image_user.use_auto_refresh

		return {'FINISHED'}


def FMDL_Texture_Load_Ftex_Button(self, context):
	self.layout.operator(FMDL_Texture_Load_Ftex.bl_idname)


class FMDL_Texture_Panel(bpy.types.Panel):
	bl_label = "FMDL Texture Settings"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "texture"

	@classmethod
	def poll(cls, context):
		return context.texture != None

	def draw(self, context):
		row = self.layout.row()
		box = self.layout.box()
		box.alignment = 'CENTER'
		texture = context.texture
		row = box.row(align=0)
		row.label(text="Image File")
		row.operator(FMDL_Scene_Open_Image.bl_idname, icon="FILESEL")
		row.operator("edit.operator", text="", icon="SEQ_SPLITVIEW")
		row.operator("reload.operator", text="", icon="FILE_REFRESH")
		row = box.row(align=0)
		row.prop(texture, "fmdl_texture_role", text="Role")
		row = box.row(align=0)
		row.prop(texture, "fmdl_texture_filename", text="Filename")
		row = box.row(align=0)
		row.prop(texture, "fmdl_texture_directory", text="Directory")


	def execute(self, context):
		# Avoids a blender bug in which an invalid image can't be replaced with a valid one
		context.texture.image_user.use_auto_refresh = context.texture.image_user.use_auto_refresh

		return {'FINISHED'}


class FMDL_MaterialParameter(bpy.types.PropertyGroup):
	name = bpy.props.StringProperty(name="Parameter Name")
	parameters = bpy.props.FloatVectorProperty(name="Parameter Values", size=4, default=[0.0, 0.0, 0.0, 0.0])

vertexGroupSummaryCache = {}

def pesBoneList(skeletonType):
	parts = skeletonType.split('_', 1)
	if len(parts) != 2:
		return None
	pesVersion = parts[0]
	bodyPart = parts[1]
	if pesVersion not in PesSkeletonData.skeletonBones:
		return None
	if bodyPart not in PesSkeletonData.skeletonBones[pesVersion]:
		return None
	return PesSkeletonData.skeletonBones[pesVersion][bodyPart]

def armatureIsPesSkeleton(armature, skeletonType):
	boneNames = pesBoneList(skeletonType)
	if boneNames is None:
		return False
	boneNames = set(boneNames)
	
	if armature.is_editmode:
		blenderBoneNames = [bone.name for bone in armature.edit_bones]
	else:
		blenderBoneNames = [bone.name for bone in armature.bones]
	for boneName in blenderBoneNames:
		if boneName not in boneNames:
			return False
	return True

def FMDL_Scene_Skeleton_update_type(scene, context):
	newType = scene.fmdl_skeleton_type
	for object in scene.objects:
		if object.type == 'ARMATURE':
			if object.fmdl_skeleton_replace_type != newType:
				object.fmdl_skeleton_replace = armatureIsPesSkeleton(object.data, newType)
				object.fmdl_skeleton_replace_type = newType

def FMDL_Scene_Skeleton_get_replace(armatureObject):
	skeletonType = bpy.context.scene.fmdl_skeleton_type
	if (
		   'fmdl_skeleton_replace' not in armatureObject
		or 'fmdl_skeleton_replace_type' not in armatureObject
		or armatureObject.fmdl_skeleton_replace_type != skeletonType
	):
		return armatureIsPesSkeleton(armatureObject.data, bpy.context.scene.fmdl_skeleton_type)
	return armatureObject.fmdl_skeleton_replace

def FMDL_Scene_Skeleton_set_replace(armatureObject, enabled):
	armatureObject.fmdl_skeleton_replace_type = bpy.context.scene.fmdl_skeleton_type
	armatureObject.fmdl_skeleton_replace = enabled

class FMDL_Scene_Skeleton_List(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		row = layout.row(align = True)
		row.prop(item, 'fmdl_skeleton_replace_effective', text = '')
		row.label(text = FMDL_Scene_Skeleton_List.objectName(item))
	
	def filter_items(self, context, data, propname):
		filterList = []
		names = {}
		
		for blenderObject in data.objects:
			if blenderObject.type == 'ARMATURE':
				filterList.append(self.bitflag_filter_item)
				names[blenderObject] = FMDL_Scene_Skeleton_List.objectName(blenderObject)
			else:
				filterList.append(0)
		
		indices = {}
		for name in sorted(list(names.values())):
			indices[name] = len(indices)
		
		sortList = []
		for blenderObject in data.objects:
			if blenderObject in names:
				sortList.append(indices[names[blenderObject]])
			else:
				sortList.append(-1)
		
		return (filterList, sortList)
	
	def objectName(blenderObject):
		if blenderObject.parent is None:
			return blenderObject.name
		else:
			return "%s :: %s" % (FMDL_Scene_Skeleton_List.objectName(blenderObject.parent), blenderObject.name)

def addBone(blenderArmature, bone, boneIDs, bonesByName):
	if bone in boneIDs:
		return boneIDs[bone]
	
	useConnect = False
	if bone.name in PesSkeletonData.bones:
		pesBone = PesSkeletonData.bones[bone.name]
		(headX, headY, headZ) = pesBone.startPosition
		(tailX, tailY, tailZ) = pesBone.endPosition
		head = (headX, -headZ, headY)
		tail = (tailX, -tailZ, tailY)
		parentBoneName = pesBone.renderParent
		while parentBoneName is not None and parentBoneName not in bonesByName:
			parentBoneName = PesSkeletonData.bones[parentBoneName].renderParent
		if parentBoneName is None:
			parentBone = None
		else:
			parentBone = bonesByName[parentBoneName]
			parentDistanceSquared = sum(((PesSkeletonData.bones[parentBoneName].endPosition[i] - pesBone.startPosition[i]) ** 2 for i in range(3)))
			if parentBoneName == pesBone.renderParent and parentDistanceSquared < 0.0000000001:
				useConnect = True
	else:
		tail = (bone.globalPosition.x, -bone.globalPosition.z, bone.globalPosition.y)
		head = (bone.localPosition.x, -bone.localPosition.z, bone.localPosition.y)
		parentBone = bone.parent
	
	if parentBone != None:
		parentBoneID = addBone(blenderArmature, parentBone, boneIDs, bonesByName)
	else:
		parentBoneID = None
	
	if sum(((tail[i] - head[i]) ** 2 for i in range(3))) < 0.0000000001:
		tail = (head[0], head[1], head[2] - 0.00001)
	
	blenderEditBone = blenderArmature.edit_bones.new(bone.name)
	boneID = blenderEditBone.name
	boneIDs[bone] = boneID
	
	blenderEditBone.head = head
	blenderEditBone.tail = tail
	blenderEditBone.hide = False
	if parentBoneID != None:
		blenderEditBone.parent = blenderArmature.edit_bones[parentBoneID]
		blenderEditBone.use_connect = useConnect
	
	return boneID

def createPesBone(blenderArmature, boneName, boneNames):
	if boneName not in PesSkeletonData.bones:
		return
	if boneName in blenderArmature.edit_bones:
		return
	
	pesBone = PesSkeletonData.bones[boneName]
	parentBoneName = pesBone.renderParent
	while parentBoneName is not None and parentBoneName not in boneNames:
		parentBoneName = PesSkeletonData.bones[parentBoneName].renderParent
	if parentBoneName is not None:
		parentDistanceSquared = sum(((PesSkeletonData.bones[parentBoneName].endPosition[i] - pesBone.startPosition[i]) ** 2 for i in range(3)))
		useConnect = (parentBoneName == pesBone.renderParent and parentDistanceSquared < 0.0000000001)
		createPesBone(blenderArmature, parentBoneName, boneNames)
	
	(headX, headY, headZ) = pesBone.startPosition
	(tailX, tailY, tailZ) = pesBone.endPosition
	head = (headX, -headZ, headY)
	tail = (tailX, -tailZ, tailY)
	if sum(((tail[i] - head[i]) ** 2 for i in range(3))) < 0.0000000001:
		tail = (head[0], head[1], head[2] - 0.00001)
	
	blenderEditBone = blenderArmature.edit_bones.new(boneName)
	blenderEditBone.head = head
	blenderEditBone.tail = tail
	blenderEditBone.hide = False
	if parentBoneName is not None:
		blenderEditBone.parent = blenderArmature.edit_bones[parentBoneName]
		blenderEditBone.use_connect = useConnect

def createPesSkeleton(context, skeletonType):
	boneNames = pesBoneList(skeletonType)
	
	armatureName = "Skeleton"
	for enumItem in bpy.types.Scene.bl_rna.properties['fmdl_skeleton_type'].enum_items:
		if enumItem.identifier == skeletonType:
			armatureName = enumItem.name
			break
	blenderArmature = bpy.data.armatures.new(armatureName)
	blenderArmature.show_names = True
	
	blenderArmatureObject = bpy.data.objects.new(armatureName, blenderArmature)
	armatureObjectID = blenderArmatureObject.name
	
	context.scene.objects.link(blenderArmatureObject)
	context.scene.objects.active = blenderArmatureObject
	bpy.ops.object.mode_set(context.copy(), mode = 'EDIT')
	
	boneIDs = {}
	for boneName in boneNames:
		createPesBone(blenderArmature, boneName, boneNames)
	
	bpy.ops.object.mode_set(context.copy(), mode = 'OBJECT')
	context.scene.update()
	return (armatureObjectID, armatureName)

def replaceArmatures(context, armatureObjectID, preferredName):
	remapList = []
	for object in bpy.data.objects:
		if (
				object.type == 'ARMATURE'
			and object.fmdl_skeleton_replace_effective
			and object.name != armatureObjectID
		):
			remapList.append(object.name)
	
	parentObjectID = None
	if len(remapList) == 1:
		preferredName = remapList[0]
		parent = bpy.data.objects[remapList[0]].parent
		if parent is not None:
			parentObjectID = parent.name
	
	for objectID in remapList:
		oldArmatureObject = bpy.data.objects[objectID]
		oldArmature = oldArmatureObject.data
		
		oldArmature.user_remap(bpy.data.objects[armatureObjectID].data)
		bpy.data.armatures.remove(oldArmature)
		
		context.scene.objects.unlink(oldArmatureObject)
		oldArmatureObject.user_remap(bpy.data.objects[armatureObjectID])
		bpy.data.objects.remove(oldArmatureObject)
	if parentObjectID is not None:
		bpy.data.objects[armatureObjectID].parent = bpy.data.objects[parentObjectID]
	bpy.data.objects[armatureObjectID].name = preferredName
	context.scene.update()

class FMDL_Scene_Skeleton_Create(bpy.types.Operator):
	"""Create PES skeleton"""
	bl_idname = "fmdl.skeleton_create"
	bl_label = "Create Skeleton"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'
	
	def execute(self, context):
		createPesSkeleton(context, context.scene.fmdl_skeleton_type)
		return {'FINISHED'}

class FMDL_Scene_Skeleton_CreateReplace(bpy.types.Operator):
	"""Create PES skeleton and replace existing"""
	bl_idname = "fmdl.skeleton_create_replace"
	bl_label = "Create and replace existing:"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'
	
	def execute(self, context):
		(newArmatureObjectID, preferredName) = createPesSkeleton(context, context.scene.fmdl_skeleton_type)
		replaceArmatures(context, newArmatureObjectID, preferredName)
		return {'FINISHED'}

class FMDL_Scene_Skeleton_Panel(bpy.types.Panel):
	bl_label = "FMDL Skeleton"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_context = "objectmode"
	bl_category = "Tools"
	
	@classmethod
	def poll(cls, context):
		return context.scene != None
	
	def draw(self, context):
		scene = context.scene
		self.layout.prop(scene, 'fmdl_skeleton_type', text = "Skeleton Type")
		self.layout.operator(FMDL_Scene_Skeleton_Create.bl_idname)
		self.layout.operator(FMDL_Scene_Skeleton_CreateReplace.bl_idname)
		self.layout.template_list(
			FMDL_Scene_Skeleton_List.__name__,
			"FMDL_Scene_Skeleton",
			scene,
			"objects",
			scene,
			"fmdl_skeleton_replace_active",
			rows = 5
		)

class FMDL_Externally_Edit(bpy.types.Operator):
	"""Edit texture with externally editor"""
	bl_idname = "edit.operator"
	bl_label = "Externally Editor"

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		texname = bpy.context.active_object.active_material.active_texture.name
		fileName = str()
		imagePath = str()
		try:
			fileName = str(texname).split()[1]
			imagePath = bpy.data.images[fileName].filepath
		except:
			pass
		if os.path.isfile(imagePath):
			bpy.ops.image.external_edit(filepath=imagePath)
		else:
			self.report({"WARNING"}, "File not found!!")
			return {'CANCELLED'}
		
		return {'FINISHED'}

	pass

class FMDL_Shader_Set(bpy.types.Operator):
	"""Set a Shader from list"""
	bl_idname = "shader.operator"
	bl_label = "Set Shader"

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		PesFoxShader.setShader(self, context)
		return {'FINISHED'}
	pass

class FMDL_Reload_Image(bpy.types.Operator):
	"""Reload All Image Texture"""
	bl_idname = "reload.operator"
	bl_label = str()

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		for image in bpy.data.images:
			if image.users:
				bpy.ops.object.mode_set(mode='EDIT')
				image.reload()
				bpy.ops.object.mode_set(mode='OBJECT')
		self.report({"INFO"}, "All image texture reloaded!")
		return {'FINISHED'}
	pass


class Fmdl_UIPanel(bpy.types.Panel):
	bl_label = "eFootball PES2021 Face/Hair Modifier"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bpy.types.Scene.face_path = StringProperty(name="FACE File", subtype='FILE_PATH', default="Face file path --->")
	bpy.types.Scene.hair_path = StringProperty(name="HAIR File", subtype='FILE_PATH', default="Hair file path --->")
	bpy.types.Scene.oral_path = StringProperty(name="ORAL File", subtype='FILE_PATH', default="Oral file path --->")
	bpy.types.Scene.autohair = BoolProperty(name="", default=True)
	bpy.types.Scene.autooral = BoolProperty(name="", default=True)
	bpy.types.Scene.idread = BoolProperty(name="", default=True)
	bpy.types.Scene.fpk_cnf = BoolProperty(name="", default=True)
	bpy.types.Scene.cnf = BoolProperty(name="", default=True)
	bpy.types.Scene.face_cnf = BoolProperty(name="", default=True)
	bpy.types.Scene.hair_cnf = BoolProperty(name="", default=True)
	bpy.types.Scene.convertftex = BoolProperty(name="",description="Convert texture dds file to ftex when you Create .FPK File.", default=False)
	bpy.types.Scene.oldid = StringProperty(name="",  default="0000")
	bpy.types.Scene.newid = StringProperty(name="",  default="0000")
	extensions_enabled = bpy.props.BoolProperty(name="Enable PES FMDL extensions", default=True)
	loop_preservation = bpy.props.BoolProperty(name="Preserve split vertices", default=True)
	mesh_splitting = bpy.props.BoolProperty(name="Autosplit overlarge meshes", default=True)
	load_textures = bpy.props.BoolProperty(name="Load textures", default=True)
	import_all_bounding_boxes = bpy.props.BoolProperty(name="Import all bounding boxes", default=False)

	global facepath, hairpath, oralpath, packfpk, pes_diff_fname
	

	def draw(self, context):
		layout = self.layout
		scn = context.scene
		facepath = scn.face_path
		oralpath = facepath[:-14] + "oral.fmdl"
		packfpk = facepath[:-23] + "face.fpk.xml"
		pes_diff_fname = facepath[:-14] + "face_diff.bin"
		box = layout.box()
		box.alignment = 'CENTER'
		row = box.row(align=0)
		this_icon = icons_collections["custom_icons"]["icon_1"].icon_id
		row.label(text="eFootball PES2021 Face/Hair Modifier", icon_value=this_icon)
		row = box.row()
		this_icon = icons_collections["custom_icons"]["icon_0"].icon_id
		row.label(text="Made by: MjTs-140914 / the4chancup", icon_value=this_icon)
		row = box.row()
		box.label(text="This Tool Works with Only Blender v2.79 (v1.93.7b)", icon="BLENDER")
		row = box.row()
		row.operator("primary.operator", text="Start New Scene").face_opname = "newscene"
		row = box.row()
		row.prop(scn, "parent_list")
		row.operator("primary.operator", text="", icon="FILE_PARENT").face_opname = "set_parent"
		row = box.row(align=0)
		row = layout.row()
		box = layout.box()
		row = box.row(align=0)
		row.label(text="EXTRACT FACE.FPK")
		row = box.row(align=0)
		row.operator(FMDL_Scene_Extract_Fpk.bl_idname)
		row = layout.row()
		box = layout.box()
		row = box.row(align=0)
		row.label(text="FMDL Import / Export Settings")
		row = box.row(align=0)
		row.menu(FMDL_Scene_Panel_FMDL_Import_Settings.__name__, icon='COLLAPSEMENU', text="Import Settings")
		row.menu(FMDL_Scene_Panel_FMDL_Export_Settings.__name__, icon='COLLAPSEMENU', text="Export Settings")
		row = layout.row()
		box = layout.box()
		row = box.row(align=1)
		row.label(text="FACE .FMDL File")

		row = box.row(align=0)
		if 'face_high' not in scn.face_path:
			row.enabled = 0
		else:
			if not os.path.isfile(facepath):
				row.enabled = 0

		row.operator("primary.operator", text="Import FACE", icon="IMPORT").face_opname = "import_face"
		row.operator("primary.operator", text="Export FACE", icon="EXPORT").face_opname = "export_face"
		row = box.row(align=0)

		row = layout.row()
		box = layout.box()
		row = box.row(align=1)
		row.label(text="HAIR .FMDL File")
		row.prop(scn, "autohair" , text="Use Same Folder")
		row = box.row()
		row = box.row(align=0)
		if scn.autohair == False:
			box.prop(scn, "hair_path", text="")
			row = box.row()
			if 'hair_high' not in scn.hair_path:
				row.enabled = 0
			hairpath = scn.hair_path
		else:
			hairpath = facepath[:-14] + "hair_high.fmdl"
			row = box.row()
			if not os.path.isfile(hairpath):
				if os.path.isfile(facepath) and 'fmdl' in facepath:
					row.label(text="hair_high.fmdl not available in current directories", icon="ERROR")
				row = box.row()
				row.enabled = 0
		if not 'face_high' in scn.face_path:
			row.enabled = 0
		row.operator("primary.operator", text="Import HAIR", icon="IMPORT").face_opname = "import_hair"
		row.operator("primary.operator", text="Export HAIR", icon="EXPORT").face_opname = "export_hair"
		row = box.row(align=0)

		row = layout.row()
		box = layout.box()
		row = box.row(align=1)
		row.label(text="ORAL .FMDL File")
		row.prop(scn, "autooral", text="Use Same Folder")
		row = box.row(align=0)
		if scn.autooral == False:
			box.prop(scn, "oral_path", text="")
			row = box.row()
			if 'oral' not in scn.oral_path:
				row.enabled = 0
			oralpath = scn.oral_path
		else:
			oralpath = facepath[:-14] + "oral.fmdl"
			row = box.row()
			if not os.path.isfile(oralpath):
				if os.path.isfile(facepath) and 'fmdl' in facepath:
					row.label(text="oral.fmdl not available in current directories", icon="ERROR")
				row = box.row()
				row.enabled = 0
		if not 'face_high' in scn.face_path:
			row.enabled = 0
		row.operator("primary.operator", text="Import ORAL", icon="IMPORT").face_opname = "import_oral"
		row.operator("primary.operator", text="Export ORAL", icon="EXPORT").face_opname = "export_oral"
		row = box.row(align=0)

		if not os.path.isfile(pes_diff_fname):
			if not os.path.isfile(pes_diff_fname) and os.path.isfile(facepath) and 'fmdl' in facepath:
				row.label(text="face_diff.bin not available in current directories", icon="ERROR")
			row = box.row()
			row.enabled = 0
		if not os.path.isfile(oralpath) and os.path.isfile(facepath) and 'fmdl' in facepath:
			row.label(text="Mouth set position now available!", icon="FILE_TICK")
			row = box.row()

		if context.mode != "OBJECT":
			row.enabled = 0
		row.prop(scn, "eyes_size")
		row = box.row()
		if not os.path.isfile(pes_diff_fname):
			if not os.path.isfile(pes_diff_fname) and os.path.isfile(facepath) and 'fmdl' in facepath:
				row.label(text="face_diff.bin not available in current directories", icon="ERROR")
			row = box.row()
			row.enabled = 0
		if not 'face_high' in scn.face_path:
			row.enabled = 0
		row.operator("primary.operator", text="Import PES_DIFF.BIN", icon="IMPORT").face_opname = "pes_diff_imp"
		row.operator("primary.operator", text="Export PES_DIFF.BIN", icon="EXPORT").face_opname = "pes_diff_exp"
		row = box.row()
		row = box.row(align=0)
		row = layout.row()
		box = layout.box()
		row = box.row()
		row.label(text="ID Relinker")
		row = box.row()
		if not 'face_high' in scn.face_path:
			row.enabled = 0
		if scn.idread == False:
			row.enabled = 0
		row.prop(scn, "newid", text="New ID")
		row.operator("primary.operator", text="", icon="FILE_REFRESH").face_opname = "IDRelink"
		row = box.row() 
		box = layout.box()
		row = box.row(align=1)
		if not os.path.isfile(packfpk):
			row.enabled = 0
		row.prop(scn, "convertftex", text="Convert .DDS File to .FTEX File")
		row = box.row()
		row.label(text="Create .FPK File")
		row.label(text="Clear Unused File")
		row = box.row()
		if not os.path.isfile(packfpk):
			row.enabled = 0
		row.operator("primary.operator", text="Create FACE.FPK File", icon="PACKAGE").face_opname = "pack_fpk"
		row.operator("primary.operator", text="Clear Unused File", icon="CANCEL").face_opname = "clr_file"
		row = box.row()
		box = layout.box()
		row = box.row()
		row.operator("wm.url_open", text='MjTs-140914 Facebook',
					 icon="URL").url = 'https://web.facebook.com/MjTs140914/'
		row.operator("wm.url_open", text='Visit Github Update',
					 icon="URL").url = 'https://github.com/MjTs140914/PES_Face_Hair_Modifier'

class Tool_Main_Operator(bpy.types.Operator):
	"""Face / Hair Modifier Tools"""
	bl_idname = "primary.operator"
	bl_label = str()
	face_opname = StringProperty()

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		global facepath, hairpath, oralpath, packfpk, unusedfile, pes_diff_bin_data
		scn = context.scene
		facepath = scn.face_path
		packfpk = facepath[:-23] + "face.fpk.xml"
		dirpath = facepath[:-29] + "\\sourceimages\\#windx11"
		pes_diff_fname = facepath[:-14] + "face_diff.bin"
		fileName = scn.face_path
		unusedfile = facepath[:-15]
		if scn.autohair == False:
			hairpath = scn.hair_path
		else:
			hairpath = facepath[:-14] + "hair_high.fmdl"
		if scn.autooral == False:
			oralpath = scn.oral_path
		else:
			oralpath = facepath[:-14] + "oral.fmdl"

		if self.face_opname == "import_face":
			if not "face_high" in bpy.data.objects:
				pes_diff_bin_data.clear()
				importFmdlfile(fileName, "Skeleton_Face", "mesh_id_face", "face_high")
				self.report({"INFO"}, "Face Imported Succesfully")
				oldIDread()
				if scn.idread == False:
					self.report({"ERROR"}, "Can't read Old ID, you can't Relink ID rightnow!")
					print("Can't read Old ID, you can't Relink ID rightnow!")
				print("Face Imported Succesfully")

			else:
				self.report({"WARNING"}, "Face Already Imported!!")
			return {'FINISHED'}

		if self.face_opname == "export_face":
			if "face_high" in bpy.data.objects:
				for child_name in ('face_high','MESH_face_high', 'MESH_face_parts'):
					for ob in bpy.data.objects[child_name].children:
						if ob.type == 'MESH' and ob.data is not None:
							uv = bpy.data.meshes[ob.data.name].uv_layers
							mat = bpy.data.objects[ob.name].material_slots
							if len(uv) == 0:
								print("Mesh [%s] does not have a primary UV map set!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] does not have a primary UV map set!" % ob.name)	
								return {'CANCELLED'}
							elif len(uv) >= 3:
								print("Mesh [%s] too much UVMap slots, need to remove!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] too much UVMap slots, need to remove!" % ob.name)	
								return {'CANCELLED'}
							elif len(uv) == 1:
								if uv[0].name != 'UVMap':
									print("Mesh [%s] UVMap name isn't correct!" % ob.name)
									self.report({"WARNING"}, "Mesh [%s] UVMap name isn't correct!" % ob.name)
									return {'CANCELLED'}
							elif len(uv) == 2:
								if uv[1].name != 'normal_map':
									print("Mesh [%s] normal_map name isn't correct!" % ob.name)
									self.report({"WARNING"}, "Mesh [%s] normal_map name isn't correct!" % ob.name)
									return {'CANCELLED'}
							if len(mat) == 0:
								print("Mesh [%s] does not have an associated material!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] does not have an associated material!" % ob.name)
								return {'CANCELLED'}
							if len(mat) >= 2:
								print("Mesh [%s] too much material slots need to remove!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] too much material slots need to remove!" % ob.name)
								return {'CANCELLED'}
				try:
					materialname("mesh_id_face_0", "fox_skin_mat")
				except:
					pass

				exportFmdlfile(fileName, "mesh_id_face", "face_high")
				self.report({"INFO"}, "Face Exported Succesfully")
				scn.face_cnf = True
				print("Face Exported Succesfully")
			else:
				self.report({"WARNING"}, "Import Face before export!!")
			return {'FINISHED'}

		if self.face_opname == "import_hair":
			if not "hair_high" in bpy.data.objects:
				pes_diff_bin_data.clear()
				fileName = hairpath
				importFmdlfile(fileName, "Skeleton_Hair", "mesh_id_hair", "hair_high")
				oldIDread()
				self.report({"INFO"}, "Hair Imported Succesfully")
				print("Hair Inported Succesfully")
				if scn.idread == False:
					self.report({"ERROR"}, "Can't read Old ID, you can't Relink ID rightnow!")
					print("Can't read Old ID, you can't Relink ID rightnow!")
			else:
				self.report({"WARNING"}, "Hair Already Imported!!")
			return {'FINISHED'}

		if self.face_opname == "export_hair":
			if "hair_high" in bpy.data.objects:
				for child_name in ('hair_high','MESH_hair_high'):
					for ob in bpy.data.objects[child_name].children:
						if ob.type == 'MESH' and ob.data is not None:
							uv = bpy.data.meshes[ob.data.name].uv_layers
							mat = bpy.data.objects[ob.name].material_slots
							if len(uv) == 0:
								print("Mesh [%s] does not have a primary UV map set!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] does not have a primary UV map set!" % ob.name)	
								return {'CANCELLED'}
							elif len(uv) >= 3:
								print("Mesh [%s] too much UVMap slots, need to remove!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] too much UVMap slots, need to remove!" % ob.name)	
								return {'CANCELLED'}
							elif len(uv) == 1:
								if uv[0].name != 'UVMap':
									print("Mesh [%s] UVMap name isn't correct!" % ob.name)
									self.report({"WARNING"}, "Mesh [%s] UVMap name isn't correct!" % ob.name)
									return {'CANCELLED'}
							elif len(uv) == 2:
								if uv[1].name != 'normal_map':
									print("Mesh [%s] normal_map name isn't correct!" % ob.name)
									self.report({"WARNING"}, "Mesh [%s] normal_map name isn't correct!" % ob.name)
									return {'CANCELLED'}
							if len(mat) == 0:
								print("Mesh [%s] does not have an associated material!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] does not have an associated material!" % ob.name)
								return {'CANCELLED'}
							if len(mat) >= 2:
								print("Mesh [%s] too much material slots need to remove!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] too much material slots need to remove!" % ob.name)
								return {'CANCELLED'}
				try:
					materialname("mesh_id_hair_0", "fox_skin_mat")
				except:
					pass

				exportFmdlfile(hairpath, "mesh_id_hair", "hair_high")
				scn.hair_cnf = True
				self.report({"INFO"}, "Hair Exported Succesfully")
				print("Hair Exported Succesfully")
			else:
				self.report({"WARNING"}, "Import Hair before export!!")
			return {'FINISHED'}

		if self.face_opname == "import_oral":
			if not "oral_high" in bpy.data.objects:
				pes_diff_bin_data.clear()
				fileName = oralpath
				importFmdlfile(fileName, "Skeleton_Oral", "mesh_id_oral", "oral_high")
				self.report({"INFO"}, "Oral Imported Succesfully")
				print("Oral Inported Succesfully")
			else:
				self.report({"WARNING"}, "Oral Already Imported!!")
			return {'FINISHED'}
		if self.face_opname == "export_oral":
			if "oral_high" in bpy.data.objects:
				for ob in bpy.data.objects['oral_high'].children:
					if ob.type == 'MESH' and ob.data is not None:
						uv = bpy.data.meshes[ob.data.name].uv_layers
						mat = bpy.data.objects[ob.name].material_slots
						if len(uv) == 0:
							print("Mesh [%s] does not have a primary UV map set!" % ob.name)
							self.report({"WARNING"}, "Mesh [%s] does not have a primary UV map set!" % ob.name)	
							return {'CANCELLED'}
						elif len(uv) >= 3:
							print("Mesh [%s] too much UVMap slots, need to remove!" % ob.name)
							self.report({"WARNING"}, "Mesh [%s] too much UVMap slots, need to remove!" % ob.name)	
							return {'CANCELLED'}
						elif len(uv) == 1:
							if uv[0].name != 'UVMap':
								print("Mesh [%s] UVMap name isn't correct!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] UVMap name isn't correct!" % ob.name)
								return {'CANCELLED'}
						elif len(uv) == 2:
							if uv[1].name != 'normal_map':
								print("Mesh [%s] normal_map name isn't correct!" % ob.name)
								self.report({"WARNING"}, "Mesh [%s] normal_map name isn't correct!" % ob.name)
								return {'CANCELLED'}
						if len(mat) == 0:
							print("Mesh [%s] does not have an associated material!" % ob.name)
							self.report({"WARNING"}, "Mesh [%s] does not have an associated material!" % ob.name)
							return {'CANCELLED'}
						if len(mat) >= 2:
							print("Mesh [%s] too much material slots need to remove!" % ob.name)
							self.report({"WARNING"}, "Mesh [%s] too much material slots need to remove!" % ob.name)
							return {'CANCELLED'}
				exportFmdlfile(oralpath, "mesh_id_oral", "oral_high")
				self.report({"INFO"}, "Oral Exported Succesfully")
				print("Oral Exported Succesfully")
			else:
				self.report({"WARNING"}, "Import Oral before export!!")
			return {'FINISHED'}

		if self.face_opname == "pack_fpk":
			if scn.face_cnf == False:
				self.report({"WARNING"}, "Face need to export!")
				return {'CANCELLED'}
			if scn.hair_cnf == False:
				self.report({"WARNING"}, "Hair need to export!")
				return {'CANCELLED'}
  
			if scn.convertftex:
				texture_covert(dirpath)
			inp_xml = ' "' + packfpk + '"'
			os.system('"' + GZSPATH + inp_xml + '"')
			scn.fpk_cnf = True
			self.report({"INFO"}, "Create FACE.FPK Succesfully")
			print("Create FACE.FPK succesfully")
			return {'FINISHED'}

		if self.face_opname == "clr_file":
			if context.scene.face_cnf == False:
				self.report({"WARNING"}, "Face ID has change you need to export!")
				return {'CANCELLED'}
			if context.scene.hair_cnf == False:
				self.report({"WARNING"}, "Hair ID has change you need to export!")
				return {'CANCELLED'}
			if context.scene.fpk_cnf == False:
				self.report({"WARNING"}, "ID has change you need to create .fpk!")
				return {'CANCELLED'}
			pes_diff_bin_data.clear()
			if os.path.isfile(packfpk):
				os.remove(packfpk)
			if os.path.exists(unusedfile):
				shutil.rmtree(unusedfile)
			remove_dds(dirpath)
			self.report({"INFO"}, "Delete Unused File Succesfully")
			print("Delete unused file succesfully")
			return {'FINISHED'}

		if self.face_opname == "pes_diff_exp":
			if len(pes_diff_bin_data) != 0:
				pes_diff_bin_exp(pes_diff_fname)
				self.report({"INFO"}, "Exporting PES_DIFF.BIN Succesfully!")
				print("Exporting PES_DIFF.BIN Succesfully!")
			else:
				self.report({"WARNING"}, "Import PES_DIFF.BIN before export!!")
				print("Import PES_DIFF.BIN before export!!")
			return {'FINISHED'}

		if self.face_opname == "pes_diff_imp":
			pes_diff_bin_imp(pes_diff_fname)
			self.report({"INFO"}, "PES_DIFF.BIN Imported Succesfully!")
			print("PES_DIFF.BIN Imported Succesfully!")
			return {'FINISHED'}
		
		if self.face_opname == "IDRelink":
			if not "face_high" in bpy.data.objects:
				self.report({"WARNING"}, "Can't relink, You need import Face!")
			elif not "hair_high" in bpy.data.objects:
				self.report({"WARNING"}, "Can't relink, You need import Hair!")
			else:
				if scn.cnf:
					try:
						NewID()
					except Exception as exception:
						self.report({"WARNING"}, format(exception))
						print(format(type(exception).__name__), format(exception))
						return {'CANCELLED'}
					self.report({"INFO"}, "Relink ID Succesfully!")
					print("Relink ID Succesfully!")
					scn.cnf = False
					scn.face_cnf = False
					scn.hair_cnf = False
					scn.fpk_cnf = False
				else:
					self.report({"WARNING"}, "ID Already relinked!")
					print("Old ID doesn't match, Please check!")
			return {'FINISHED'}

		if self.face_opname == "newscene":
			if scn.face_cnf == False:
				self.report({"WARNING"}, "Face ID has change you need to export!")
				return {'CANCELLED'}
			if scn.hair_cnf == False:
				self.report({"WARNING"}, "Hair ID has change you need to export!")
				return {'CANCELLED'}
			if scn.fpk_cnf == False:
				self.report({"WARNING"}, "ID has change you need to create .fpk!")
				return {'CANCELLED'}
			pes_diff_bin_data.clear()
			bpy.ops.wm.read_homefile()
			return {'FINISHED'}

		if self.face_opname == "set_parent":
			try:
				objects = bpy.data.objects
				parentName = objects[context.scene.parent_list]
				ob_name = objects[context.active_object.name]
				ob_name.parent = parentName
				self.report({"INFO"}, "Set parent succesfully!")		
			except Exception as exception:
				self.report({"WARNING"}, format(exception))
			return {'FINISHED'}

		if self.face_opname == "set_default_enum":
			defaultEnum(self)
			return {'FINISHED'}

	pass


classes = [

	FMDL_Scene_Open_Image,
	FMDL_Scene_Extract_Fpk,
	FMDL_Scene_Panel_FMDL_Import_Settings,
	FMDL_Scene_Panel_FMDL_Export_Settings,

	FMDL_Scene_Skeleton_List,
	FMDL_Scene_Skeleton_Create,
	FMDL_Scene_Skeleton_CreateReplace,
	FMDL_Scene_Skeleton_Panel,

	FMDL_Mesh_BoneGroup_List,
	FMDL_Mesh_BoneGroup_RemoveUnused,
	FMDL_Mesh_BoneGroup_Refresh,
	FMDL_Mesh_BoneGroup_CopyFromSelected,
	FMDL_Mesh_BoneGroup_Specials,
	FMDL_Mesh_BoneGroup_Panel,

	FMDL_Material_Parameter_List_Add,
	FMDL_Material_Parameter_List_Remove,
	FMDL_Material_Parameter_List_MoveUp,
	FMDL_Material_Parameter_List_MoveDown,
	FMDL_Material_Parameter_Name_List,
	FMDL_Material_Panel,

	FMDL_Mesh_Panel,
	FMDL_Shader_Set,
	FMDL_Externally_Edit,
	FMDL_Reload_Image,

	FMDL_Object_BoundingBox_Create,
	FMDL_Object_BoundingBox_Remove,
	FMDL_Object_BoundingBox_Panel,

	FMDL_Texture_Load_Ftex,
	FMDL_Texture_Panel,
	Fmdl_UIPanel,
	Tool_Main_Operator,

	TiNA.FMDL_TransferNormalsPanel,
	TiNA.FMDL_TransferNormals,
	TiNA.FMDL_WrapNormals,
	TiNA.FMDL_ClearNormals,


]


def register():
	skeletonTypes = []

	pcoll = bpy.utils.previews.new()
	pcoll.load("icon_0", os.path.join(icons_dir, "icon_0.dds"), 'IMAGE')
	pcoll.load("icon_1", os.path.join(icons_dir, "icon_1.dds"), 'IMAGE')
	icons_collections["custom_icons"] = pcoll

	for pesVersion in PesSkeletonData.skeletonBones:
		for skeletonType in PesSkeletonData.skeletonBones[pesVersion]:
			skeletonTypes.append(('%s_%s' % (pesVersion, skeletonType), '%s %s' % (pesVersion, skeletonType), '%s %s' % (pesVersion, skeletonType)))
	skeletonTypes.reverse()
	defaultPesVersion = list(PesSkeletonData.skeletonBones.keys())[-1]
	defaultType = list(PesSkeletonData.skeletonBones[defaultPesVersion].keys())[0]
	defaultSkeletonType = '%s_%s' % (defaultPesVersion, defaultType)


	bpy.types.Object.fmdl_file = bpy.props.BoolProperty(name="Is FMDL file", options={'SKIP_SAVE'})
	bpy.types.Object.fmdl_filename = bpy.props.StringProperty(name="FMDL filename", options={'SKIP_SAVE'})
	bpy.types.Material.fmdl_material_parameter_active = bpy.props.IntProperty(name="FMDL_Material_Parameter_Name_List index", default=-1, options={'SKIP_SAVE'})
	bpy.types.Object.fmdl_export_extensions_enabled = bpy.props.BoolProperty(name="Enable PES FMDL extensions",  default=True)
	bpy.types.Object.fmdl_export_loop_preservation = bpy.props.BoolProperty(name="Preserve split vertices",   default=True)
	bpy.types.Object.fmdl_export_mesh_splitting = bpy.props.BoolProperty(name="Autosplit overlarge meshes",   default=True)
	bpy.types.Scene.fmdl_import_extensions_enabled = bpy.props.BoolProperty(name="Enable PES FMDL extensions", default=True)
	bpy.types.Scene.fmdl_import_loop_preservation = bpy.props.BoolProperty(name="Preserve split vertices", default=True)
	bpy.types.Scene.fmdl_import_mesh_splitting = bpy.props.BoolProperty(name="Autosplit overlarge meshes", default=True)
	bpy.types.Scene.fmdl_import_load_textures = bpy.props.BoolProperty(name="Load textures", default=True)
	bpy.types.Scene.fmdl_import_all_bounding_boxes = bpy.props.BoolProperty(name="Import all bounding boxes", default=False)
	bpy.types.Scene.fixmeshesmooth = bpy.props.BoolProperty(name="FIX-Smooth Meshes", default=True)


	bpy.types.Scene.fmdl_skeleton_type = bpy.props.EnumProperty(name = "Skeleton type",
		items = skeletonTypes,
		default = defaultSkeletonType,
		update = FMDL_Scene_Skeleton_update_type,
		options = {'SKIP_SAVE'}
	)
	bpy.types.Object.fmdl_skeleton_replace = bpy.props.BoolProperty(name = "Replace skeleton", default = False, options = {'SKIP_SAVE'})
	bpy.types.Object.fmdl_skeleton_replace_type = bpy.props.EnumProperty(name = "Skeleton replacement target", items = skeletonTypes, options = {'SKIP_SAVE'})
	bpy.types.Object.fmdl_skeleton_replace_effective = bpy.props.BoolProperty(name = "Replace skeleton",
		get = FMDL_Scene_Skeleton_get_replace,
		set = FMDL_Scene_Skeleton_set_replace,
		options = {'SKIP_SAVE'}
	)
	bpy.types.Scene.fmdl_skeleton_replace_active = bpy.props.IntProperty(name = "FMDL_Scene_Skeleton_List index", default = -1, options = {'SKIP_SAVE'})
	bpy.types.Bone.fmdl_bone_in_active_mesh = bpy.props.BoolProperty(name = "Enabled",
		get = FMDL_Mesh_BoneGroup_Bone_get_enabled,
		set = FMDL_Mesh_BoneGroup_Bone_set_enabled,
		options = {'SKIP_SAVE'}
	)

	bpy.types.Scene.import_face_high = bpy.props.BoolProperty(name = "Import face_high.fmdl", default = True)
	bpy.types.Scene.import_hair_high = bpy.props.BoolProperty(name = "Import hair_high.fmdl", default = True)
	bpy.types.Scene.import_oral = bpy.props.BoolProperty(name = "Import oral.fmdl", default = True)
	bpy.types.Scene.import_pes_diff = bpy.props.BoolProperty(name="Import face_diff.bin", default=True)
	bpy.types.Scene.eyes_size = bpy.props.FloatProperty(name="Eye Size", default=1.0, min=0.5, max=2.0, update=update_eye_size)

	for c in classes:
		bpy.utils.register_class(c)

	bpy.utils.register_class(FMDL_MaterialParameter)

	bpy.types.Scene.parent_list = bpy.props.EnumProperty(name="Parent", items=PesFoxShader.parent_list, default="MESH_face_high")
	bpy.types.Mesh.fmdl_alpha_enum_select = bpy.props.EnumProperty(name="Alpha Enum", items=PesFoxShader.AlphaEnum, default="0", update=update_alpha_list)
	bpy.types.Mesh.fmdl_shadow_enum_select = bpy.props.EnumProperty(name="Shadow Enum", items=PesFoxShader.ShadowEnum, default="0", update=update_shadow_list)
	bpy.types.Mesh.fmdl_alpha_enum = bpy.props.IntProperty(name="Alpha Enum", default=0, min=0, max=255, update=update_alpha_enum)
	bpy.types.Mesh.fmdl_shadow_enum = bpy.props.IntProperty(name="Shadow Enum", default=0, min=0, max=255, update=update_shadow_enum)

	domData = parse(xml_sett)
	shaders = [(shader.getAttribute("shader"), shader.getAttribute("shader"), "Technique Type: "+shader.getAttribute("technique")) 
					for shader in domData.getElementsByTagName("FoxShader") if shader.getAttribute("shader")]
	shaders.sort(reverse=0)
	bpy.types.Material.fox_shader = bpy.props.EnumProperty(name="Select Fox Shader", items=shaders)
	bpy.types.Material.fmdl_material_shader = bpy.props.StringProperty(name="Shader", default="pes_3ddf_skin_face", update=update_shader_list)
	bpy.types.Material.fmdl_material_technique = bpy.props.StringProperty(name="Technique")
	bpy.types.Material.fmdl_material_parameters = bpy.props.CollectionProperty(name="Material Parameters", type=FMDL_MaterialParameter)
	bpy.types.Texture.fmdl_texture_filename = bpy.props.StringProperty(name="Texture Filename")
	bpy.types.Texture.fmdl_texture_directory = bpy.props.StringProperty(name="Texture Directory")
	bpy.types.Texture.fmdl_texture_role = bpy.props.StringProperty(name="Texture Role")

	bpy.types.Bone.fmdl_bone_in_active_mesh = bpy.props.BoolProperty(name = "Enabled", get = FMDL_Mesh_BoneGroup_Bone_get_enabled, set = FMDL_Mesh_BoneGroup_Bone_set_enabled, options = {'SKIP_SAVE'})
	bpy.types.Object.fmdl_bone_active = bpy.props.IntProperty(name = "FMDL_Mesh_BoneGroup_List index", default = -1, options = {'SKIP_SAVE'})
	bpy.types.Mesh.fmdl_show_vertex_group_details = bpy.props.BoolProperty(name = "Show usage details", default = True, options = {'SKIP_SAVE'})
	bpy.types.Mesh.fmdl_lock_nonempty_vertex_groups = bpy.props.BoolProperty(name = "Lock in-use bone groups", default = True, options = {'SKIP_SAVE'})
	bpy.types.Mesh.fmdl_show_vertex_group_vertices = bpy.props.BoolProperty(name = "Show vertices [v]", default = True, options = {'SKIP_SAVE'})
	bpy.types.Mesh.fmdl_show_vertex_group_weights = bpy.props.BoolProperty(name = "Show weights [w]", default = True, options = {'SKIP_SAVE'})
	bpy.types.Material.fmdl_material_parameter_active = bpy.props.IntProperty(name="FMDL_Material_Parameter_Name_List index", default=-1, options={'SKIP_SAVE'})


def unregister():
	for pcoll in icons_collections.values():
		bpy.utils.previews.remove(pcoll)
	icons_collections.clear()
	for c in classes[::-1]:
		bpy.utils.unregister_class(c)
	bpy.utils.unregister_class(FMDL_MaterialParameter)
	
