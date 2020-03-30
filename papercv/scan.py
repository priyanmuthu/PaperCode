# import the necessary packages
import numpy as np
import argparse
import cv2
import imutils
import matplotlib.pyplot as plt
import pytesseract
from pytesseract import Output
from skimage.filters import threshold_local, gaussian
from papercv.transform import four_point_transform
from papercv.swt import SWTScrubber
from papercv.utils import get_RGB_mouse_click, UtilMethods
from papercv.table import find_table_from_image, pre_process_image



def scan_page_from_image(image):
	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	orig_height = image.shape[0]
	ratio = image.shape[0] / 500.0
	orig = image.copy()
	image = imutils.resize(image, height = 500)

	# convert the image to grayscale, blur it, and find edges
	# in the image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 10, 200)
	
	# find the contours in the edged image, keeping only the
	# largest ones, and initialize the screen contour
	cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break

	# apply the four point transform to obtain a top-down
	# view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	
	# convert the warped image to grayscale, then threshold it
	# to give it that 'black and white' paper effect
	# warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	# T = threshold_local(warped, 11, offset = 10, method = "gaussian")
	# warped = (warped > T).astype("uint8") * 255

	return warped

def tesseract(image):
	d = pytesseract.image_to_data(image, output_type=Output.DICT)
	n_boxes = len(d['level'])
	print('tesseract complete')
	for i in range(n_boxes):
		(x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		print(d['conf'][i])

		if i > 30 and i < 50:
			roi = image[y:y+h, x:x+w]
			cv2.imshow('segment no:'+str(i),roi)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

	cv2.imshow('img', image)
	cv2.waitKey(0)

def text_segment(image):
	#grayscale
	gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	cv2.imshow('gray',gray)
	cv2.waitKey(0)

	#binary
	# ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
	thresh = UtilMethods.sauvola(gray)
	cv2.imshow('second',thresh)
	cv2.waitKey(0)

	#Erosion - remove thin lines
	# kernel = np.ones((1,1),np.uint8)
	# thresh = cv2.erode(thresh,kernel,iterations = 1)
	# cv2.imshow('erosion',thresh)
	# cv2.waitKey(0)

	#dilation
	kernel = np.ones((5,5), np.uint8)
	img_dilation = cv2.dilate(thresh, kernel, iterations=2)
	cv2.imshow('dilated',img_dilation)
	cv2.waitKey(0)

	#find contours
	ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	#sort contours
	sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

	for i, ctr in enumerate(sorted_ctrs):
		# Get bounding box
		x, y, w, h = cv2.boundingRect(ctr)
		
		# get the roi image and check if it has text
		# roi = image[y:y+h, x:x+w]
		# iStr = pytesseract.image_to_string(roi, lang='eng')
		# if iStr.strip() == '':
		# 	cv2.rectangle(image,(x,y),( x + w, y + h ),(90,0,255),2)

		# drawing bounding box
		cv2.rectangle(image,(x,y),( x + w, y + h ),(90,0,255),2)

		# Getting ROI
		# roi = image[y:y+h, x:x+w]
		# cv2.imshow('segment no:'+str(i),roi)
		# cv2.waitKey(0)

	cv2.imshow('marked areas',image)
	cv2.waitKey(0)

def process_image(image_path: str):
	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	image = cv2.imread(image_path)
	scanned_image = scan_page_from_image(image)
	height, width, channels = scanned_image.shape
	
	scanned_image = cv2.resize(scanned_image, (int(width/2), int(height/2)))
	text_segment(scanned_image)

	# image2 = cv2.imread('./papercv/test/warped.jpg')
	# print(image2.shape)

	# image2 = cv2.imread('./papercv/test/pup2.jpg')
	# image2 = cv2.resize(image2, (scanned_image.shape[1], scanned_image.shape[0]))
	# dilation_diff(scanned_image, image2)
	# tesseract(scanned_image)

	return scanned_image

def dilation_diff(image1, image2):
	#grayscale
	gray = cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
	gray2 = cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)
	cv2.imshow('gray',gray)
	cv2.imshow('gray2',gray2)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	#binary
	# ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
	thresh = UtilMethods.sauvola(gray)
	thresh2 = UtilMethods.sauvola(gray2)
	cv2.imshow('second',thresh)
	cv2.imshow('second2',thresh2)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	#dilation
	kernel = np.ones((5,5), np.uint8)
	img_dilation = cv2.dilate(thresh, kernel, iterations=1)
	img_dilation2 = cv2.dilate(thresh2, kernel, iterations=1)
	cv2.imshow('dilated',img_dilation)
	cv2.imshow('dilated2',img_dilation2)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	diff, thresh = UtilMethods.image_diff(img_dilation, img_dilation2)
	cv2.imshow('diff', diff)
	cv2.imshow('thresh', thresh)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def run():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required = True,
		help = "Path to the image to be scanned")
	args = vars(ap.parse_args())
	image_path = args["image"]

	im1 = cv2.imread(image_path)
	im2 = cv2.imread('./papercv/test/pup2.jpg')

	pImage = process_image(image_path)

