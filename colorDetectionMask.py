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