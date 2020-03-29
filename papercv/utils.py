import cv2


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