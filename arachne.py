# * * * * * * * * * * * * * * * * * * * * 
# * arachne.py - Feb 22, 2015
# * - Michael Snider
# * 
# * Re-draw images based on sample images
# * provided, to have it appear in a
# * different style or be composed of
# * elements from the samples
# * 
# * * * * * * * * * * * * * * * * * * * * 

import argparse
import os
import sys
import img
from img import ImgSet
from scipy import misc



def validInput(args):
	""" Test the input to decide whether or not to end early """

	valid = True

	# source.img
	if not os.path.isfile(args.src):
		print "Source image does not exist."
		valid = False

	if not ImgSet.allowedFileType(args.src):
		print "Source image is not an allowed file type:", valid_filetypes
		valid = False

	# sample/dir
	if not os.path.isdir(args.sample_dir):
		print "Sample directory does not exist."
		valid = False
	else:

		# check for at least 1 valid sample (critera, has at least one file with valid filetype)
		validSample = False

		for root, dirs, files in os.walk(args.sample_dir):
			for sample_file in files:
				if ImgSet.allowedFileType(sample_file):
					validSample = True

		if not validSample:
			print "Sample directory does not contain valid samples of filetype:", valid_filetypes
			valid = False


	# destination.img
	if os.path.isfile(args.dest):
		print "Destination image already exists."
		valid = False

	if not ImgSet.allowedFileType(args.src):
		print "Destination image is not an allowed file type:", valid_filetypes
		valid = False


	return valid






def main():
	""" Main functionality for re-drawing images """

	# Handle command line arguments

	parser = argparse.ArgumentParser(description='Re-draw image using components from sample images provided')
	parser.add_argument('src', metavar='source.img', type=str, help='source image to be re-drawn')
	parser.add_argument('sample_dir', metavar='sample/dir', type=str, help='directory of sample images to re-draw source with components from')
	parser.add_argument('dest', metavar='destination.img', type=str, help='destination for re-drawn image')

	args = parser.parse_args()


	# Invalid arguments

	if not validInput(args):
		sys.exit(1)


	# Gather input into data structure

	img_set = ImgSet(src=args.src, samples=[], dest=args.dest)

	for root, dirs, files in os.walk(args.sample_dir):
			for sample_file in files:
				if ImgSet.allowedFileType(sample_file):
					img_set.samples.append(args.sample_dir + "/" + sample_file)


	# Apply technique

	output_img = img.linearConstructOnce(img_set, (3, 3))



	# Save image

	if output_img is not None:
		misc.imsave(img_set.dest, output_img)
		print "Image saved as %s" % (img_set.dest, )




if __name__ == "__main__":
	main()