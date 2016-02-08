import fnmatch
import os
import shutil

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
		"""Traverse the directory tree and get a list of all 
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
		# order preserving removal of duplicates
		# CREDITS: http://www.peterbe.com/plog/uniqifiers-benchmark
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