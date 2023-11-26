import cv2
import numpy as np

def showPixelValue(event,x,y,flags,param):
    global frame, combinedResult, placeholder
    frame_height, frame_width = frame.shape[:2]

    if x > frame_width - 1 or y > frame_height - 1: return
    if event == cv2.EVENT_MOUSEMOVE:
        bgr = frame[y,x]

        ycb = cv2.cvtColor(np.uint8([[bgr]]),cv2.COLOR_BGR2YCrCb)[0][0]
        lab = cv2.cvtColor(np.uint8([[bgr]]),cv2.COLOR_BGR2Lab)[0][0]
        hsv = cv2.cvtColor(np.uint8([[bgr]]),cv2.COLOR_BGR2HSV)[0][0]
        
        placeholder = np.zeros((frame.shape[0],400,3),dtype=np.uint8)

        cv2.putText(placeholder, "BGR {}".format(bgr), (20, 70), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(placeholder, "HSV {}".format(hsv), (20, 140), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(placeholder, "YCrCb {}".format(ycb), (20, 210), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(placeholder, "LAB {}".format(lab), (20, 280), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        
        combinedResult = np.hstack([frame,placeholder])
        
        cv2.imshow('Color ranges',combinedResult)


if __name__ == '__main__' :
    global frame
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Can\'t capture camera")
        exit()

    ret, frame = cap.read()
    if not ret:
        print("Can\'t receive frame")
        exit()

    cv2.namedWindow('Color ranges')
    cv2.setMouseCallback('Color ranges', showPixelValue)
    cv2.imshow('Color ranges',frame)

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

'''
import cv2
import numpy as np

def nothing(x):
    pass

cv2.namedWindow('frame')

cv2.createTrackbar('HMin', 'frame', 0, 255, nothing)
cv2.createTrackbar('SMin', 'frame', 0, 255, nothing)
cv2.createTrackbar('VMin', 'frame', 0, 255, nothing)
cv2.createTrackbar('HMax', 'frame', 0, 179, nothing)
cv2.createTrackbar('SMax', 'frame', 0, 255, nothing)
cv2.createTrackbar('VMax', 'frame', 0, 255, nothing)

cv2.setTrackbarPos('HMax', 'frame', 179)
cv2.setTrackbarPos('SMax', 'frame', 255)
cv2.setTrackbarPos('VMax', 'frame', 255)

hMin = sMin = vMin = hMax = sMax = vMax = 0
phMin = psMin = pvMin = phMax = psMax = pvMax = 0

wait_time = 33

cap = cv2.VideoCapture(0)

while(1):
    ret,frame = cap.read()
    frame = cv2.flip(frame,1)
    output = frame

    hMin = cv2.getTrackbarPos('HMin', 'frame')
    sMin = cv2.getTrackbarPos('SMin', 'frame')
    vMin = cv2.getTrackbarPos('VMin', 'frame')

    hMax = cv2.getTrackbarPos('HMax', 'frame')
    sMax = cv2.getTrackbarPos('SMax', 'frame')
    vMax = cv2.getTrackbarPos('VMax', 'frame')

    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(frame,frame, mask= mask)

    if( (phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
        print("[%d,%d,%d],[%d,%d,%d]" % (hMin , sMin , vMin, hMax, sMax , vMax))
        phMin = hMin
        psMin = sMin
        pvMin = vMin
        phMax = hMax
        psMax = sMax
        pvMax = vMax

    cv2.imshow('frame',output)

    if cv2.waitKey(wait_time) & 0xFF == 27:
        break

cv2.destroyAllWindows()
'''
