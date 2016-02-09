import fnmatch
import os
import shutil

# These are designators that are used to re-name the media files
#  A - area, I - Internal, F - Defect, and P - Pipe
DESIGNATORS = {
	'AreaDesignator':'A', 
	'InternalDesignator':'I', 
	'DefectDesignator':'F', 
	'PipeDesignator':'P' 
	}


class MCAImage(object):
	"""An image handling object for PipeTech Mobile export project data. 
	This class takes a filepath to a folder containing
	(a) MS Access database file
	(b) several sub-folders containing jpeg images whose relative
	paths are stored in the database file.

	MCAImage implements traversal of the sub-folders to find and list all 
	the jpeg images, remaming of the images based on related information in 
	the database and update the references in the database

	This is done while (optionally) relocating all the renamed images to a
	new folder
	"""

	def __init__(self, rootPath="/", pattern="*.jpg"):
		self.rootPath = rootPath
		self.pattern = pattern
		self.fileList = []
		self._build_file_list()

	def get_file_list(self, tailpart=False):
		"""Traverse the directory tree and returns a list of all 
		the files in all the subdirectories. Return an array of 
		filenames with path based on rootPath. 

		If tailpart == True then strip the directory part off the 
		file paths
		"""
		if self.fileList == None:
			self.fileList = self._build_file_list()

		# if tailpart is true
		if tailpart:
			truncated = []
			for item in self.fileList:
				dirpart, filepart = os.path.split(item)
				truncated.append(filepart)
			return truncated

		return self.fileList


	def _build_file_list(self):
		"""refreshes or builds the file list"""
		if len(self.fileList) > 0:
			del self.fileList[:]

		for root, dirs, files in os.walk(self.rootPath):
			for filename in fnmatch.filter(files, self.pattern):
				self.fileList.append(os.path.join(root, filename))

	def copy_to(self, dst):
		"""Copy the files from rootPath directory (and subdirectories) 
		to the destination 'dst'. Do not recreate any subdirectories.
		The shutil.copy2 function is used. This function copies all
		metadata 
		"""
		# does dst path exist?
		dest = ''
		src = self.rootPath
		if os.path.exists(dst):
			# path exists => is this absolute or relative
			drive, tail = os.path.splitdrive(dst)
			if not drive:
				# ensure creating a subfolder relative to rootPath 
				destination, tailpart = os.path.split(dst)
				dest = os.path.join(os.path.dirname(self.rootPath, tailpart))
			else:
				# drive letter found - maybe Windows system
				# designate this the output path
				dest = os.path.realpath(dst)
		else:
			dest = os.path.realpath(dst)

		# count the files
		fileCount = 0
		for root, dirs, files in os.walk(self.rootPath):
			for filename in fnmatch.filter(files, self.pattern):
				src_file = os.path.join(root, filename)
				dst_file = os.path.join(dest, filename)
				shutil.copy2(src_file, dst_file)
				fileCount += 1

		return fileCount


	def inspection_from_filename(self, filename):
		"""Extract the inspection id from a single filename
		Format: "inspection-12575_image_Header.1.jpg", i.e.
		"inspection-<inspection id>_image_Header.1.jpg"
		"""
		result = None
		try:
			result = str(filename.split('_')[0].split('-')[1])
		finally:
			return result


	def inspections_from_filenames(self, list_of_files, unique=True):
		"""Given a list of filenames of format "inspection-12575_image_Header.1.jpg",
		iterate the list, extract the number portion from each filename and
		append to a list, insp_list
		"""
		insp_list = []
		for filename in list_of_files:
			insp_list.append(filename.split('_')[0].split('-')[1])

		if unique:
			return self.remove_duplicates(insp_list)
		return insp_list


	def remove_duplicates(self, seq, idfun=None):
		# CREDITS: "http://www.peterbe.com/plog/uniqifiers-benchmark"
		# order preserving removal of duplicates
		
	    if idfun is None:
	    	def idfun(x): return x

	    seen = {}
	    result = []

	    for item in seq:
			marker = idfun(item)
			
			# but in new ones:
			if marker in seen: 
				continue
			seen[marker] = 1
			result.append(item)
	    return result


	def stats(self):
		"""Calculate and return a list of metrics on the data:
		inspectionCount: total number of inspections,
		fileCount: number of image files
		folderPath: root path to the image files
		"""
		fileList = self.get_file_list(True)
		inspectionList = self.inspections_from_filenames(fileList)
		# number of items(files)
		fileCount = len(fileList)
		inspectionCount = len(inspectionList)
		# get the folder path from one of the items in self.fileList
		# folderPath = os.path.split(self.fileList[0])[0]
		folderPath = os.path.normpath(os.path.dirname(self.fileList[0]))

		result = {
			"fileCount":fileCount, 
			"inspectionCount":inspectionCount,
			"folderPath":folderPath
			}

		return result


	def list_by_inspection(self):
		"""Return a dictionary of images grouped by inspection, i.e.
		{insp1:[img1, img2, img3,..], insp2:[img1, img2, img3,..], etc}

		File-renaming designators used on items of format "inspection-12575_image_Header.1.jpg"
		correspond with: 0 = Area, 1 = Area, 2 = Internal, 3+ = Defect
		**** CHANGE THIS RULE IF THE PROJECT SPECIFICATIONS CHANGE ****
		"""
		designator_rule = ('AreaDesignator', 'AreaDesignator', 'InternalDesignator', 'DefectDesignator')

		lbi_dict = dict()
		# get a list of image filenames - i.e. without the folder part
		filelist = self.get_file_list(True)
		# get a list of unique inspection numbers - these will be dictionary keys in lbi_dict
		inspectionList = self.inspections_from_filenames(filelist)
		# the increment entity on the filename (0,1,2,etc) translates to (001,002,003,etc) on rename
		position = "001"
		# for each image in list of images
		for imagename in filelist:
			# parse imagename to get the inspection using self.inspection_from_filename(imagename)
			inspection = str(self.inspection_from_filename(imagename))
			increment = "{}".format(str(imagename.split('.')[1]))
			if int(increment) >= len(designator_rule):
				designator = DESIGNATORS[designator_rule[len(designator_rule) - 1]]
			elif int(increment) >= 0:
				designator = DESIGNATORS[designator_rule[int(increment)]]
			else:
				designator = DESIGNATORS[designator_rule[0]]

			# if there is already an entry in the dictionary for this record, then append
			if inspection in lbi_dict:
				position = "{:0>3d}".format(len(lbi_dict[inspection]) + 1)
			else:
				lbi_dict[inspection] = []

			# lbi_dict[inspection] = [(inspection, imagename, designator, position, increment)]
			# TODO: add new name = MHID_<designator>_position.jpg to the tuple
			lbi_dict[inspection].append( (inspection, imagename, designator, position, increment) )
				
		
		return lbi_dict

		
	def sort_by_key(self, adict):
		"""Sort a dictionary of values by the keys"""
		dict_sorted_by_key = sorted(adict.items(), key = lambda t: t[0])
		return dict_sorted_by_key

