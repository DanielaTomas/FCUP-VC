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

    #result = np.zeros_like(frame)

    squares_found = 0
    
    for lower_range, upper_range, color_name in color_ranges:
        mask = cv2.inRange(hsv_frame, np.array(lower_range), np.array(upper_range))
        
        #res = cv2.bitwise_and(frame, frame, mask=mask)
        #cv2.imshow(color_name,res)
        #result = cv2.add(result, res)

        blurred_frame = cv2.GaussianBlur(mask, (5, 5), 0)

        kernel = np.ones((5, 5), np.uint8)
        blurred_frame = cv2.morphologyEx(blurred_frame, cv2.MORPH_OPEN, kernel)
        blurred_frame = cv2.morphologyEx(blurred_frame, cv2.MORPH_CLOSE, kernel)

        edges = cv2.Canny(blurred_frame, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #contours, _ = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

        #cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
        
        #cv2.imshow("Combined Result", result)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500 and area < 3000:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if is_square(approx):
                    squares_found += 1
                    # draw rectangles
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    face_colors.append((color_name, (x, y)))

    if squares_found == 9:
        face_colors.sort(key=lambda x: x[1][1]) # sort by y
        groups = [face_colors[i:i + 3] for i in range(0, len(face_colors), 3)] # split into groups of three
        # sort each group by x
        for group in groups:
            group.sort(key=lambda x: x[1][0])

        if groups not in face: #TODO
            face.append(groups)
            print(f"{groups[1][1][0]} face detected!")
            
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
    for groups in face:
        print(f"{groups[1][1][0]} face")
        for group in groups:
            for color, coordinates in group:
                print(f"  Color: {color}, Coordinates: {coordinates}")
    

if __name__ == "__main__":
    main()