import cv2 as cv
import numpy as np

def find_rubiks_cube(frame):
    # Convert the frame to grayscale for easier processing
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
    # Perform edge detection
    edges = cv.Canny(blurred, 50, 200)
    
    # Find contours in the edge-detected image
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    #cv.drawContours(frame, contours, -1, (0,255,0), 3)

    cv.imshow('Original', frame)
    cv.imshow('Gray', gray)
    cv.imshow('Blurred', blurred)
    cv.imshow('Edges', edges)

    
    for contour in contours:
        # Approximate the contour as a polygon
        epsilon = 0.05 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        
        # If the polygon has 4 vertices, it may be the Rubik's Cube
        if len(approx) == 4 and cv.contourArea(approx) > 500 and cv.contourArea(approx) < 3000:
            # Draw a bounding rectangle around the detected cube
            x, y, w, h = cv.boundingRect(approx)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Calculate the center of the Rubik's Cube
            center_x = x + w // 2
            center_y = y + h // 2
            cv.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
            
            # You can continue from here to detect and process the cube faces
        
    return frame

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Can't capture camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame.")
        break

    # Call the function to find and highlight the Rubik's Cube
    frame_with_cube = find_rubiks_cube(frame)

    cv.imshow('Rubik\'s Cube Detection', frame_with_cube)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
