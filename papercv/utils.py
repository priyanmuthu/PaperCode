import cv2
import numpy as np
from skimage.filters import threshold_otsu, threshold_niblack, threshold_sauvola
from pyzbar.pyzbar import decode

frame = None

def mouseRGB(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        global frame
        if len(frame.shape) == 2:
            print('Grascale value: ', frame[y,x])
        else:
            colorsB = frame[y,x,0]
            colorsG = frame[y,x,1]
            colorsR = frame[y,x,2]
            colors = frame[y,x]
            print("Red: ",colorsR)
            print("Green: ",colorsG)
            print("Blue: ",colorsB)
            print("BRG Format: ",colors)
        print("Coordinates of pixel: X: ",x,"Y: ",y)

def get_RGB_mouse_click(image):
    global frame
    frame = image
    cv2.namedWindow('mouseRGB')
    cv2.setMouseCallback('mouseRGB',mouseRGB)
    cv2.imshow('mouseRGB', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


class UtilMethods:

    @staticmethod
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
    
    @staticmethod
    def denoise(image):
        imcpy = image.copy()

        if len(imcpy.shape) == 2:
            imcpy = cv2.fastNlMeansDenoising(imcpy,None,10,7,21)
        elif len(imcpy.shape) == 3:
            imcpy = cv2.fastNlMeansDenoisingColored(imcpy,None,10,10,7,21)
        
        return imcpy
    
    @staticmethod
    def image_diff(image1, image2):

        # Ensure the image is already in grayscale and denoised
        # image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        # image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # image1 = denoise(image1)
        # image2 = denoise(image2)

        # resize
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

        # diff = cv2.absdiff(image2, image1)
        diff = cv2.absdiff(image1, image2)
        # diff = cv2.absdiff(image1, image2)
        # mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        res, thresh = cv2.threshold(diff, 150, 255, cv2.THRESH_BINARY)
        
        return diff, thresh
    
    @staticmethod
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
    
    @staticmethod
    def increase_image_brigtness(img, value):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:,:,2] += value
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    @staticmethod
    def decode_qr_code(image):
        qr_decoded = decode(image)[0]
        return qr_decoded.data, qr_decoded.rect