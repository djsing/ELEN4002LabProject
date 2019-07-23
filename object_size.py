# USAGE
# python object_size.py --image images/example_01.png --width 0.955
# python object_size.py --image images/example_02.png --width 0.955
# python object_size.py --image images/example_03.png --width 3.5

# import the necessary packages
# import tensorflow
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import matplotlib.pyplot as plt
import preprocessing
import edgeDetection

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("-w", "--width", type=float, required=True,
	help="width of the left-most object in the image (in meters)")
args = vars(ap.parse_args())

# convert image to grayscale, and blur it to remove some noise
image = cv2.imread(args["image"])
gray = preprocessing.blurImage(image)

# perform edge detection, then rough image closing to complete edges
edged = edgeDetection.gray2binaryEdgedImage(gray)
# # find contours in the edge map
# cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
# 	cv2.CHAIN_APPROX_SIMPLE)
# cnts = imutils.grab_contours(cnts)

# # sort the contours from left-to-right and initialize the
# # 'pixels per metric' calibration variable
# (cnts, _) = contours.sort_contours(cnts)
contours = edgeDetection.returnContours(edged)
pixelsPerMetric = None

# loop over the contours individually
for c in contours:
	# if the contour is not sufficiently large, ignore it
	if cv2.contourArea(c) < 2000:
		continue

	# compute the rotated bounding box of the contour
	orig = image.copy()
	box = cv2.minAreaRect(c)
	box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
	box = np.array(box, dtype="int")

	print(cv2.contourArea(c))
	# plot pixels
	# contourCoordinates = [item[0] for item in c]
	# xcoordinates = [item[0] for item in contourCoordinates]
	# ycoordinates = [item[1] for item in contourCoordinates]
	# plt.scatter(xcoordinates, ycoordinates)
	# plt.show()
	cv2.drawContours(orig, c, -1, (0, 255, 0), 2)

	# order the points in the contour such that they appear
	# in top-left, top-right, bottom-right, and bottom-left
	# order, then draw the outline of the rotated bounding
	# box
	box = perspective.order_points(box)
	cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

	# loop over the original points and draw them
	for (x, y) in box:
		cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

	# unpack the ordered bounding box, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates
	(tl, tr, br, bl) = box
	(tltrX, tltrY) = midpoint(tl, tr)
	(blbrX, blbrY) = midpoint(bl, br)

	# compute the midpoint between the top-left and top-right points,
	# followed by the midpoint between the top-righ and bottom-right
	(tlblX, tlblY) = midpoint(tl, bl)
	(trbrX, trbrY) = midpoint(tr, br)

	# draw the midpoints on the image
	cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

	# draw lines between the midpoints
	cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
		(255, 0, 255), 2)
	cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
		(255, 0, 255), 2)

	# compute the Euclidean distance between the midpoints
	dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
	dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

	# if the pixels per metric has not been initialized, then
	# compute it as the ratio of pixels to supplied metric
	# (in this case, inches)
	if pixelsPerMetric is None:
		pixelsPerMetric = dB / args["width"]
		print('pixelspermetric is ', pixelsPerMetric)

	# compute the size of the object
	dimA = dA / pixelsPerMetric
	dimB = dB / pixelsPerMetric

	# draw the object sizes on the image
	cv2.putText(orig, "{:.1f}cm".format(dimA),
		(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (255, 255, 255), 2)
	cv2.putText(orig, "{:.1f}cm".format(dimB),
		(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (255, 255, 255), 2)

	# show the output image
	cv2.imshow("Image", orig)
	
	# cimg = np.zeros_like(orig)
	# cv2.drawContours(cimg, c, -1, color=255, thickness=-1)
	# cv2.imshow("bin", cimg)

	# mask = np.zeros(orig.shape,np.uint8)
	# cv2.drawContours(mask,c,0,255,-1)
	# pixelpoints = cv2.findNonZero(mask)
	# print(pixelpoints)

	# create a simple mask image similar 
	# to the loaded image, with the  
	# shape and return type 
	maskOrig = image.copy()
	mask = np.zeros(maskOrig.shape[:2], np.uint8) 
   
	# specify the background and foreground model 
	# using numpy the array is constructed of 1 row 
	# and 65 columns, and all array elements are 0 
	# Data type for the array is np.float64 (default) 
	backgroundModel = np.zeros((1, 65), np.float64) 
	foregroundModel = np.zeros((1, 65), np.float64) 
   
	# define the Region of Interest (ROI) 
	# as the coordinates of the rectangle 
	# where the values are entered as 
	# (startingPoint_x, startingPoint_y, width, height) 
	# these coordinates are according to the input image 
	# it may vary for different images 
	rectangle = (tl[0], tl[1], tr[0] - tl[0], bl[1] - tl[1]) 
	# apply the grabcut algorithm with appropriate 
	# values as parameters, number of iterations = 3  
	# cv2.GC_INIT_WITH_RECT is used because 
	# of the rectangle mode is used  
	cv2.grabCut(maskOrig, mask, rectangle, backgroundModel, foregroundModel, 3, cv2.GC_INIT_WITH_RECT) 
	mask2 = np.where((mask == 2)|(mask == 0), 0, 1).astype('uint8') 
	maskOrig = maskOrig * mask2[:, :, np.newaxis]
	cv2.imshow('mask', maskOrig) 
	# plt.colorbar() 
	# plt.show() 
	cv2.waitKey(0)