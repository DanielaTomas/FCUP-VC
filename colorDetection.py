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
    cap.release()
    cv2.destroyAllWindows()