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
