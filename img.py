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
from patch import BestPatch
from patch import ImgSet
from patch import SplitPatchInfo
from patch import SamplePatches



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


	# Get ndarray for image
	img_read = misc.imread(img_set.src)

	if patch_size[0] > img_read.shape[1] or patch_size[1] > img_read.shape[0]:
		print "Patch size larger than image"
		return None

	# Set up blank canvas
	img_write = numpy.zeros(img_read.shape, dtype=img_read.dtype)



	# Get patch info
	splitPatchInfo = SplitPatchInfo(img_read, patch_size)
	print splitPatchInfo

	# Set up sample patches
	samplePatches = SamplePatches(img_set, img_read)



	# Iterate over src patches
	for source_patch, bounds in splitPatchInfo:

		print "Patch %d" % (splitPatchInfo.currentPatchNum, )

		# use best patch to overwrite
		bounds.boundWrite(img_write, BestPatch.getBestPatch(source_patch, samplePatches))




	return img_write

