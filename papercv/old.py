def cognitive_service(image_body: str):

	with open('./papercv/test/test1.jpg', mode='rb') as file: # b is important -> binary
		fileContent = file.read()

	headers = {
		# Request headers
		'Content-Type': 'application/octet-stream',
		# 'Content-Type': 'application/json',
		'Ocp-Apim-Subscription-Key': '3fb10260d6854b598edbc676f9518dcc',
	}

	params = urllib.parse.urlencode({
		# Request parameters
		# 'mode': 'Handwritten',
		'mode': 'Printed',
	})

	try:
		conn = http.client.HTTPSConnection('eastus.api.cognitive.microsoft.com')
		conn.request("POST", "/vision/v2.0/recognizeText?%s" % params, fileContent, headers)
		# conn.request("POST", "/vision/v2.0/recognizeText?%s" % params, '{"url":"https://media.npr.org/assets/img/2016/04/17/handwritten-note_wide-941ca37f3638dca912c8b9efda05ee9fefbf3147.jpg"}', headers)
		response = conn.getresponse()
		data = response.read()
		print(data)
		conn.close()
	except Exception as e:
		print("[Errno {0}] {1}".format(e.errno, e.strerror))


def find_line_nos(image):
	
	gray = dilate_image(image)
	
	# ret, thresh = cv2.threshold(gray,80,255,cv2.THRESH_BINARY_INV)
	# ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
	# edges = cv2.Canny(gray,50,150,apertureSize = 3)
	# norm_image = cv2.normalize(gray, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
	# norm_image = cv2.equalizeHist(gray)
	# sobelx = cv2.Sobel(gray,cv2.CV_64F,1,0,ksize=5)
	# sobely = cv2.Sobel(gray,cv2.CV_64F,0,1,ksize=5)
	print('showing image')
	cv2.imshow("test1", gray)
	# cv2.imshow("tes	t1", edges)
	# cv2.imshow("test2", norm_image)
	# cv2.imshow("test1", sobelx)
	# cv2.imshow("test2", sobely)
	cv2.waitKey(0)