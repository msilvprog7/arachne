# * * * * * * * * * * * * * * * * * * * * 
# * patch.py - March 5, 2015
# * - Michael Snider
# * 
# * Patch components and classes
# * 
# * * * * * * * * * * * * * * * * * * * *
from scipy import misc
import numpy
import math
import copy


class ImgSet:
	""" Data structure to contain core components required
		such as source image, sample images, and destination
		for re-drawn image.
	"""

	valid_filetypes = ['jpg', 'png']


	def __init__(self, src='', samples=[], dest=''):
		""" Constructor """

		self.src = src
		self.samples = samples
		self.dest = dest


	@staticmethod
	def allowedFileType(filename):
		""" Check if filename ends with valid filetype """

		for filetype in ImgSet.valid_filetypes:

			if filename.endswith("." + filetype):
				return True


		return False



class PatchUtilities:
	""" Additional functions useful when working with patches """

	@staticmethod
	def upperBound(value, upperValue):
		""" Cap the value by upperValue, can be no more than it """

		if value > upperValue:
			return upperValue

		return value



class Patch:
	""" Collection of pixels from an image """

	def __init__(self, pixels=None):
		""" Constructor """

		self.pixels = pixels


	def getPatchSize(self):
		""" Return (px_width, px_height) of patch """
		return (self.pixels.shape[1], self.pixels.shape[0])


	@staticmethod
	def numPatches(img_arr, patch_size):
		""" Get the number of patches that will result from dividing the
			image array into patches of the specified size
		"""

		return int(Patch.patchCols(img_arr, patch_size) * Patch.patchRows(img_arr, patch_size))


	@staticmethod
	def patchCols(img_arr, patch_size):
		""" Get the number of patch columns that will result from dividing the
			image array into patches of the specified size
		"""

		return int(math.ceil(float(img_arr.shape[1]) / patch_size[0]))
	

	@staticmethod
	def patchRows(img_arr, patch_size):
		""" Get the number of patch rows that will result from dividing the
			image array into patches of the specified size
		"""

		return int(math.ceil(float(img_arr.shape[0]) / patch_size[1]))


	@staticmethod
	def comparePatches(a, b):
		""" Compare same sized patches a and b based on avg pixel value """

		if a.pixels.shape != b.pixels.shape:
			return 0.0

		pixel_val_sum = 0.0

		for y in range(a.pixels.shape[0]):
			for x in range(a.pixels.shape[1]):
				pixel_val_sum += Patch.comparePixels(a.pixels[y, x], b.pixels[y, x])

		return (pixel_val_sum / (a.pixels.shape[0] * a.pixels.shape[1]))


	@staticmethod
	def comparePixels(a, b):
		""" Compare pixels based on avg of components raised to a power """


		pixel_sum = 0.0

		for i in range(len(a)):
			pixel_sum += abs(int(a[i]) - int(b[i]))

		return 1.0 - (pixel_sum / (len(a) * 255))


	@staticmethod
	def permute(patch):
		""" Return a list of all rotated and flipped patches of same dimensions """

		ret_patches = []
		rot_patches = [patch]

		curr_patch = copy.deepcopy(patch)


		# rotations

		for i in range(3):

			curr_patch.pixels = numpy.rot90(curr_patch.pixels)

			if (curr_patch.pixels.shape == patch.pixels.shape):
				rot_patches.append(copy.deepcopy(curr_patch))

		# flipped
		for rot_patch in rot_patches:

			ret_patches.append(copy.deepcopy(rot_patch))

			rot_patch.pixels = numpy.fliplr(rot_patch.pixels)
			ret_patches.append(rot_patch)

		return ret_patches




class PatchBounds:
	""" Storage class for the bounds of a patch on the original image """

	def __init__(self):
		""" Constructor """

		self.startPxRow = 0
		self.endPxRow = 0
		self.startPxCol = 0
		self.endPxCol = 0


	def boundCopy(self, img):
		""" Copy subsection of img specified by bounds """

		return img[self.startPxRow:self.endPxRow, self.startPxCol:self.endPxCol].copy()


	def boundWrite(self, img_write, from_patch):
		""" Write values from patch to img_write over bounds on img_write """

		if from_patch is None:
			return

		for y in range(self.startPxRow, self.endPxRow):
			for x in range(self.startPxCol, self.endPxCol):
				img_write[y, x] = from_patch.pixels[y - self.startPxRow, x - self.startPxCol]



class BestPatch:
	""" Contain functionality for finding the best patch closest to the specified patch """

	@staticmethod
	def getBestPatch(patch, samplePatches):
		""" Get closest Patch to patch in samplePatches
		"""

		bestPatch = None
		bestValue = 0.0

		samplePatches.setPatchSize(patch)

		# iterate over sample images to find best patch to represent in
		for curr_patch in samplePatches:

			currentValue = Patch.comparePatches(patch, curr_patch)

			if currentValue > bestValue:
				bestValue = currentValue
				bestPatch = curr_patch

		return bestPatch



class SplitPatchInfo:
	""" Handle generation of patch information for an image where patches are split from
		the image, meaning the pixels within a patch only belong within that patch (dividing
		the image into patches)
	"""

	def __init__(self, img_read, patch_size):
		""" Constructor """

		self.img = img_read
		self.general_patch_size = patch_size

		self.currentPatchNum = -1
		self.currentPatch = None

		self.numPatches = Patch.numPatches(img_read, patch_size)
		self.patchRows = Patch.patchRows(img_read, patch_size)
		self.patchCols = Patch.patchCols(img_read, patch_size)


	def __str__(self):
		""" Print """
		return str(self.numPatches) + " " + str(self.patchRows) + " " + str(self.patchCols)


	def __iter__(self):
		""" Iterator - iterates over patches """
		return self


	def next(self):
		""" Grab next patch """

		self.currentPatchNum += 1

		# Stop iteration if exceeded number of patches
		if self.currentPatchNum >= self.numPatches:
			raise StopIteration
			return


		patchRow = self.currentPatchNum // self.patchCols
		patchCol = self.currentPatchNum % self.patchCols

		# bounds of patch
		bounds = PatchBounds()

		bounds.startPxRow = int(patchRow * self.general_patch_size[1])
		bounds.endPxRow = PatchUtilities.upperBound(bounds.startPxRow + self.general_patch_size[1], self.img.shape[0])
		bounds.startPxCol = int(patchCol * self.general_patch_size[0])
		bounds.endPxCol = PatchUtilities.upperBound(bounds.startPxCol + self.general_patch_size[0], self.img.shape[1])


		# get pixels in current patch
		self.currentPatch = Patch(pixels=bounds.boundCopy(self.img))

		return self.currentPatch, bounds



class SamplePatches:
	""" A way of consolidating how sample patches are generated and managed """

	def __init__(self, img_set, img_read):
		""" Constructor """

		self.imgSet = img_set
		self.imgRead = img_read
		self.samplePatches = {}

		self.iter_patch_size = (0, 0)
		self.iter_counter = -1
		self.iter_max = 0


	def generate(self, source_patch):
		""" Generate sample patches if needed.
			Returns number of sample patches matching 
			patch size of source patch.
		"""

		self.iter_patch_size = source_patch.getPatchSize()
		currKey = self.iter_patch_size

		if currKey in self.samplePatches:
			return len(self.samplePatches[currKey])

		
		self.samplePatches[currKey] = []

		print "Creating samples ", currKey

		# Construct patches
		for sampleImg in self.imgSet.samples:

			print sampleImg
			
			sampleImgRead = misc.imread(sampleImg)

			# doesn't match how pixels are encoded, move on
			if (sampleImgRead.shape[2] != self.imgRead.shape[2] or sampleImgRead.dtype != self.imgRead.dtype):
				continue

			# iterate over pixels, act as upper left corner of patch
			for y in range(sampleImgRead.shape[0] - (self.iter_patch_size[1] - 1)):

				for x in range(sampleImgRead.shape[1] - (self.iter_patch_size[0] - 1)):

					samplePatch = Patch(pixels=sampleImgRead[y:(y + self.iter_patch_size[1]), x:(x + self.iter_patch_size[0])])
					self.addPatch(currKey, samplePatch)

					# get rotated and flipped patches as well
					# permutedPatches = Patch.permute(samplePatch)
					# self.addPatch(currKey, permutedPatches)


		return len(self.samplePatches[currKey])


	def addPatch(self, key, patch):
		""" Add sample to list of samples """

		self.samplePatches[key].append(patch)


	def setPatchSize(self, source_patch):
		""" Pass in a patch to specify patch size for sample patch generation and 
			then this is usable for iteration 
		"""

		self.iter_counter = -1
		self.iter_max = self.generate(source_patch)


	def __iter__(self):
		""" Iterator - iterate over sample patches with patch size set using setPatchSize """
		return self


	def next(self):
		""" Grab next patch with patch size specified """

		self.iter_counter += 1

		if self.iter_counter >= self.iter_max:
			self.iter_counter = -1
			raise StopIteration

		return self.samplePatches[self.iter_patch_size][self.iter_counter]


