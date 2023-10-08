import cv2
import numpy as np

# HSV format
color_ranges = [
    ((160, 100, 100), (180, 255, 255), "Red"),
    ((30, 100, 100), (99, 255, 255), "Green"),
    ((100, 100, 100), (130, 255, 255),"Blue"),
    ((21, 100, 100), (35, 255, 255), "Yellow"),
    ((0, 0, 120), (179, 50, 255), "White"),
    ((5, 100, 100), (20, 255, 255), "Orange")
]


def is_square(approx):
    if len(approx) == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if aspect_ratio >= 0.95 and aspect_ratio <= 1.05:
            return True
    return False


face = []
def find_rubiks_cube(frame): # find and highlight the Rubik's Cube pieces
    
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    face_colors = []

    for lower_range, upper_range, color_name in color_ranges:
        mask = cv2.inRange(hsv_frame, np.array(lower_range), np.array(upper_range))

        blurred_frame = cv2.GaussianBlur(mask, (5, 5), 0)

        kernel = np.ones((5, 5), np.uint8)
        blurred_frame = cv2.erode(blurred_frame, kernel, iterations=1)
        blurred_frame = cv2.dilate(blurred_frame, kernel, iterations=1)

        edges = cv2.Canny(blurred_frame, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        squares_found = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area > 500 and area < 3000:
                epsilon = 0.05 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if is_square(approx):
                    squares_found += 1
                    # draw rectangles
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    face_colors.append(color_name) #TODO guardar também coodenadas e ordena-las depois

        if squares_found == 9: #TODO and set(face) == set(face_colors)
            face.append(list(face_colors))
            print("detected all the pieces of this face")
            
    return frame


def main():

    cap = cv2.VideoCapture(0) # initialize the camera

    if not cap.isOpened():
        print("Can\'t capture camera")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can\'t receive frame")
            break

        frame_with_cube = find_rubiks_cube(frame)

        cv2.imshow("Rubik\'s Cube Detection", frame_with_cube)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # print
    for i, colors in enumerate(face):
        print(f"Colors in face {i + 1}: {', '.join(colors)}")

if __name__ == "__main__":
    main()