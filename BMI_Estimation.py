from findPerson import findPersonInPhoto as persons
from findPerson import personArea, maskThickness
from referenceObject import findReferenceObject as findRef
import cv2

def gen():
	import argparse
	import csv
	import os
	
	ap = argparse.ArgumentParser()
	ap.add_argument("-w", "--width", type=float, required=True, help="width of the left-most object in the image (in meters)")
	ap.add_argument("-v", "--visualise", nargs='?', const=True, type=bool, required=False, default=False, help="show all images etc.")
	ap.add_argument("-m", "--mask", nargs='?', const=True, type=bool, required=False, default=False, help="show masks on images.")
	args = vars(ap.parse_args())

	csvFrontFile = open('front.csv', 'w', newline='')
	csvSideFile = open('side.csv', 'w', newline='')
	frontWriter = csv.writer(csvFrontFile, delimiter=',')
	sideWriter = csv.writer(csvSideFile, delimiter=',')
	listOfFrontImages = []
	listOfFrontImageNames = []
	listOfSideImages = []
	listOfSideImageNames = []
	widths = []
	depths= []

	print('[INFO] Reading Images')
	for filename in os.listdir('images'):
		if os.path.isdir('images/' + filename):
			continue

		image = cv2.imread('images/' + filename)
		if 'Front' in filename or 'F' in filename:
			listOfFrontImages.append(image)
			listOfFrontImageNames.append(filename)
		elif 'Side' in filename or 'S' in filename:
			listOfSideImages.append(image)
			listOfSideImageNames.append(filename)

	print('[INFO] Extracting Front Masks')
	listOfFrontBinMasks = persons(listOfFrontImages, args["visualise"], args["mask"])
	print('[INFO] Extracting Side Masks')
	listOfSideBinMasks = persons(listOfSideImages, args["visualise"], args["mask"])
	print('[INFO] Finding Front Ref. Metric')
	listOfFrontPixelsPerMetric = findRef(listOfFrontImages, args["width"], args["visualise"], args["mask"], listOfFrontImageNames)
	print('[INFO] Finding Side Ref. Metric')
	listOfSidePixelsPerMetric = findRef(listOfSideImages, args["width"], args["visualise"], args["mask"], listOfSideImageNames)
	print('[INFO] Finding Widths')
	widths = maskThickness(listOfFrontBinMasks, listOfFrontPixelsPerMetric)
	print('[INFO] Finding Depths')
	depths = maskThickness(listOfSideBinMasks, listOfSidePixelsPerMetric)

	for width, depth in zip(widths, depths):
		frontWriter.writerow(width)
		sideWriter.writerow(depth)
	csvFrontFile.close()
	csvSideFile.close()

def detect(args):
	print("Detect Mode, Arguments: ", args)
	# save images in root folder
	fImage = cv2.imread(args['fimg'])
	sImage = cv2.imread(args['simg'])
	print('[INFO] Finding Front and Side Masks')
	listOfPixelsPerMetric, listOfBinMasks = extractMasks([fImage, sImage], args)
	print('[INFO] Extracting Front and Side Dimensions')
	dimensions = maskThickness(listOfBinMasks, listOfPixelsPerMetric)
	frontImageDimensions = dimensions[0]
	sideImageDimensions = dimensions[1]
	cv2.destroyAllWindows()

	return frontImageDimensions, sideImageDimensions

def extractMasks(listOfImages, args):
	listOfBinMasks = persons(listOfImages, args["visualise"], args["mask"])
	listOfPixelsPerMetric = findRef(listOfImages, args["width"], args["visualise"], args["mask"], [args['fimg'], args['simg']])
	return listOfPixelsPerMetric, listOfBinMasks

if __name__ == "__main__" : gen()