# * * * * * * * * * * * * * * * * * * * * 
# * img.py - Feb 22, 2015
# * - Michael Snider
# * 
# * Image re-drawing components and
# * operations for Arachne
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
				pixel_val_sum += Patch.comparePixels(a.pixels[x, y], b.pixels[x, y])

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







def upperBound(value, upperValue):
	""" Cap the value by upperValue, can be no more than it """

	if value > upperValue:
		return upperValue

	return value




# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
# * Techniques/Operations

def linear(img_set, patch_size):
	""" Linear comparison of samples to source with specified patch size (px_width, px_height)
		This is a VERY slow operation.
	"""

	# Valid input

	if not isinstance(img_set, ImgSet):
		print "img_set in img.linear() must be of type img.ImgSet"
		return None

	if not isinstance(patch_size, tuple) or len(patch_size) != 2 or not isinstance(patch_size[0], int) or not isinstance(patch_size[1], int):
		print "patch_size in img.linear() must be a tuple of 2 ints"
		return None


	# Get ndarrays

	img_read = misc.imread(img_set.src)

	if patch_size[0] > img_read.shape[1] or patch_size[1] > img_read.shape[0]:
		print "Patch size larger than image"
		return None


	# Set up blank canvas

	img_write = numpy.zeros(img_read.shape, dtype=img_read.dtype)


	# Get patch info

	numPatches = Patch.numPatches(img_read, patch_size)
	patchRows = Patch.patchRows(img_read, patch_size)
	patchCols = Patch.patchCols(img_read, patch_size)

	print numPatches, patchRows, patchCols

	for patchNum in range(numPatches):

		print "Patch %d" % (patchNum, )

		patchRow = patchNum // patchCols
		patchCol = patchNum % patchCols


		# bounds of patch

		startPxRow = int(patchRow * patch_size[1])
		endPxRow = upperBound(startPxRow + patch_size[1], img_read.shape[0])

		startPxCol = int(patchCol * patch_size[0])
		endPxCol = upperBound(startPxCol + patch_size[0], img_read.shape[1])


		# get pixels in current patch

		source_patch = Patch(pixels=img_read[startPxRow:endPxRow, startPxCol:endPxCol].copy())
		

		# iterate over sample images to find best patch to represent in

		bestPatch = None
		bestValue = 0.0

		for sample_image in img_set.samples:

			sample_image_read = misc.imread(sample_image)

			# doesn't match how pixels are encoded, move on
			if (sample_image_read.shape[2] != img_read.shape[2] or sample_image_read.dtype != img_read.dtype):
				continue

			# iterate over pixels, act as upper left corner of patch
			for y in range(sample_image_read.shape[0] - (patch_size[1] - 1)):

				for x in range(sample_image_read.shape[1] - (patch_size[0] - 1)):

					sample_patch = Patch(pixels=sample_image_read[y:(y + patch_size[1]), x:(x + patch_size[0])])

					# all permutations makes this INCREDIBLY slow
					# get rotated and flipped patches as well
					# sample_patches = Patch.permute(sample_patch)
					sample_patches = [sample_patch]

					for curr_patch in sample_patches:
						currentValue = Patch.comparePatches(source_patch, curr_patch)

						if currentValue > bestValue:
							bestValue = currentValue
							bestPatch = curr_patch


		# use best patch to overwrite
		if bestPatch is not None:

			for y in range(startPxRow, endPxRow):
				for x in range(startPxCol, endPxCol):
					img_write[y, x] = bestPatch.pixels[y - startPxRow, x - startPxCol]




	return img_write



def linearConstructOnce(img_set, patch_size):
	""" Linear comparison of samples to source with specified patch size (px_width, px_height)
		but constructing patches of samples only once if necessary.
	"""

	# Valid input

	if not isinstance(img_set, ImgSet):
		print "img_set in img.linearConstructOnce() must be of type img.ImgSet"
		return None

	if not isinstance(patch_size, tuple) or len(patch_size) != 2 or not isinstance(patch_size[0], int) or not isinstance(patch_size[1], int):
		print "patch_size in img.linearConstructOnce() must be a tuple of 2 ints"
		return None


	# Get ndarrays

	img_read = misc.imread(img_set.src)

	if patch_size[0] > img_read.shape[1] or patch_size[1] > img_read.shape[0]:
		print "Patch size larger than image"
		return None


	# Set up blank canvas

	img_write = numpy.zeros(img_read.shape, dtype=img_read.dtype)


	# Get patch info

	numPatches = Patch.numPatches(img_read, patch_size)
	patchRows = Patch.patchRows(img_read, patch_size)
	patchCols = Patch.patchCols(img_read, patch_size)

	print numPatches, patchRows, patchCols

	# Set up dictionary for samples patches
	sample_patches = {};

	for patchNum in range(numPatches):

		print "Patch %d" % (patchNum, )

		patchRow = patchNum // patchCols
		patchCol = patchNum % patchCols


		# bounds of patch

		startPxRow = int(patchRow * patch_size[1])
		endPxRow = upperBound(startPxRow + patch_size[1], img_read.shape[0])

		startPxCol = int(patchCol * patch_size[0])
		endPxCol = upperBound(startPxCol + patch_size[0], img_read.shape[1])


		# get pixels in current patch

		source_patch = Patch(pixels=img_read[startPxRow:endPxRow, startPxCol:endPxCol].copy())
		

		# iterate over sample patches to find best patch to represent in

		bestPatch = None
		bestValue = 0.0

		for sample_image in img_set.samples:

			curr_key = (sample_image, source_patch.getPatchSize())

			if curr_key not in sample_patches:
				# Construct patches

				print "Construct sample patches", curr_key

				sample_image_read = misc.imread(sample_image)
				sample_patches[curr_key] = []

				# doesn't match how pixels are encoded, move on
				if (sample_image_read.shape[2] != img_read.shape[2] or sample_image_read.dtype != img_read.dtype):
					continue

				# iterate over pixels, act as upper left corner of patch
				for y in range(sample_image_read.shape[0] - (patch_size[1] - 1)):

					for x in range(sample_image_read.shape[1] - (patch_size[0] - 1)):

						sample_patch = Patch(pixels=sample_image_read[y:(y + patch_size[1]), x:(x + patch_size[0])])
						sample_patches[curr_key].append(sample_patch)

						# get rotated and flipped patches as well
						# sample_patches = Patch.permute(sample_patch)
						# sample_patches[curr_key].append(sample_patches)
			
			# Compare patches

			for curr_patch in sample_patches[curr_key]:
					currentValue = Patch.comparePatches(source_patch, curr_patch)

					if currentValue > bestValue:
						bestValue = currentValue
						bestPatch = curr_patch



		# use best patch to overwrite
		if bestPatch is not None:

			for y in range(startPxRow, endPxRow):
				for x in range(startPxCol, endPxCol):
					img_write[y, x] = bestPatch.pixels[y - startPxRow, x - startPxCol]




	return img_write