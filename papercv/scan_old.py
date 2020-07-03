# import the necessary packages
from papercv.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
from pyzbar.pyzbar import decode
import http.client, urllib.request, urllib.parse, urllib.error, base64
from papercv.swt import SWTScrubber
from papercv.utils import get_RGB_mouse_click
from papercv.table import find_table_from_image, pre_process_image
from skimage.filters import threshold_otsu, threshold_niblack, threshold_sauvola
import matplotlib.pyplot as plt

def increase_image_brigtness(img, value):
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	hsv[:,:,2] += value
	return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def decode_qr_code(image):
	qr_decoded = decode(image)[0]
	return qr_decoded.data, qr_decoded.rect

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
	
	# show the original image and the edge detected image
	print("STEP 1: Edge Detection")
	# cv2.imshow("Image", image)
	# cv2.imshow("Edged", edged)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	
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
		print('points: ', len(approx))
		if len(approx) == 4:
			screenCnt = approx
			break
	# show the contour (outline) of the piece of paper
	print("STEP 2: Find contours of paper")
	# cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
	# cv2.imshow("Outline", image)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

	# apply the four point transform to obtain a top-down
	# view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	# convert the warped image to grayscale, then threshold it
	# to give it that 'black and white' paper effect
	# warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	# T = threshold_local(warped, 11, offset = 10, method = "gaussian")
	# warped = (warped > T).astype("uint8") * 255
	# show the original and scanned images
	print("STEP 3: Apply perspective transform")
	# cv2.imshow("Original", orig)
	# cv2.imshow("Scanned", warped)
	# cv2.imshow("Original", imutils.resize(orig, height = orig_height))
	# cv2.imshow("Scanned", imutils.resize(warped, height = orig_height))
	# cv2.waitKey(0)

	return warped

def image_diff(image1, image2):

	image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
	image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
	image1 = denoise(image1)
	image2 = denoise(image2)

	# resize
	image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
	# cv2.imshow("diff", image1)
	# cv2.imshow("diff2", image2)
	# cv2.waitKey(0)
	# return

	diff = cv2.absdiff(image2, image1)
	# diff = cv2.absdiff(image1, image2)
	
	# diff = cv2.absdiff(image1, image2)
	# mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
	res, thresh = cv2.threshold(diff, 150, 255, cv2.THRESH_BINARY)
	cv2.imshow("diff", diff)
	cv2.imshow("thresh", thresh)
	cv2.waitKey(0)

	# get_RGB_mouse_click(diff)
	# cv2.imwrite("result.png", canvas)

def process_image(image_path: str):
	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	image = cv2.imread(image_path)
	scanned_image = scan_page_from_image(image)
	height, width, channels = scanned_image.shape
	
	scanned_image = cv2.resize(scanned_image, (int(width/2), int(height/2)))
	# retval, buffer = cv2.imencode('.jpg', scanned_image)

	return scanned_image

def find_line_nos(image):
	
	gray = dilate_image(image)
	print('showing image')
	cv2.imshow("test1", gray)
	cv2.waitKey(0)

def denoise(image):
	imcpy = image.copy()

	if len(imcpy.shape) == 2:
		imcpy = cv2.fastNlMeansDenoising(imcpy,None,10,7,21)
	elif len(imcpy.shape) == 3:
		imcpy = cv2.fastNlMeansDenoisingColored(imcpy,None,10,10,7,21)
	
	return imcpy

def dilate_image(img, morph_size=(8, 8)):
	# get rid of the color
	pre = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	pre = denoise(pre)
	# Otsu threshold
	pre = cv2.threshold(pre, 250, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	# dilate the text to make it solid spot
	cpy = pre.copy()
	struct = cv2.getStructuringElement(cv2.MORPH_RECT, morph_size)
	cpy = cv2.dilate(~cpy, struct, anchor=(-1, -1), iterations=1)
	pre = ~cpy
	return pre

def text_segment(image):
	#grayscale
	gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	cv2.imshow('gray',gray)
	cv2.waitKey(0)

	#binary
	# ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
	thresh = sauvola(gray)
	cv2.imshow('second',thresh)
	cv2.waitKey(0)

	#dilation
	kernel = np.ones((5,5), np.uint8)
	img_dilation = cv2.dilate(thresh, kernel, iterations=1)
	cv2.imshow('dilated',img_dilation)
	cv2.waitKey(0)

	#find contours
	ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	#sort contours
	sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

	for i, ctr in enumerate(sorted_ctrs):
		# Get bounding box
		x, y, w, h = cv2.boundingRect(ctr)

		# Getting ROI
		roi = image[y:y+h, x:x+w]

		# show ROI
		cv2.rectangle(image,(x,y),( x + w, y + h ),(90,0,255),2)
		# cv2.imshow('segment no:'+str(i),roi)
		# cv2.waitKey(0)

	cv2.imshow('marked areas',image)
	cv2.waitKey(0)

def sauvola(image):
	# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# threshImage = threshold_niblack(image, 25)
	threshImage = threshold_sauvola(image, 25)
	binary_sauvola = image < threshImage

	binary_sauvola = binary_sauvola.astype(np.uint8)  #convert to an unsigned byte
	binary_sauvola*=255

	# plt.figure(figsize=(8, 7))
	# plt.subplot(2, 2, 4)
	# plt.imshow(binary_sauvola, cmap=plt.cm.gray)
	# plt.title('Sauvola Threshold')
	# plt.axis('off')
	# plt.show()
	# denoise(binary_sauvola)
	return binary_sauvola

def run():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required = True,
		help = "Path to the image to be scanned")
	args = vars(ap.parse_args())
	image_path = args["image"]

	im1 = cv2.imread(image_path)
	im2 = cv2.imread('./papercv/test/pup2.jpg')

	pImage = process_image(image_path)
	text_segment(pImage)

	# image_diff(pImage, im2)

	# # vis_image = find_table_from_image(pImage)
	# cv2.imshow('test', vis_image)
	# cv2.waitKey(0)
	# find_line_nos(pImage)
	# # get_RGB_mouse_click(pImage)