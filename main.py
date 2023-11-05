import cv2
import numpy as np
import kociemba
from steps import *

# HSV format
color_ranges = [
    ((160, 100, 100), (180, 255, 255), "Red"),
    ((30, 100, 100), (99, 255, 255), "Green"),
    ((100, 100, 100), (130, 255, 255), "Blue"),
    ((21, 100, 100), (35, 255, 255), "Yellow"),
    ((0, 0, 120), (179, 50, 255), "White"),
    ((5, 100, 100), (20, 255, 255), "Orange")
]


def is_square(approx): # check if a contour is a square
    if len(approx) == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if aspect_ratio >= 0.95 and aspect_ratio <= 1.05:
            return True
    return False


face = []


def find_face(frame): # find and highlight the Rubik's cube pieces
    
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    global face
    face_colors = []
    groups = []

    squares_found = 0
    
    for lower_range, upper_range, color_name in color_ranges:
        mask = cv2.inRange(hsv_frame, np.array(lower_range), np.array(upper_range))

        blurred_frame = cv2.GaussianBlur(mask, (5, 5), 0)

        kernel = np.ones((5, 5), np.uint8)
        blurred_frame = cv2.morphologyEx(blurred_frame, cv2.MORPH_OPEN, kernel)
        blurred_frame = cv2.morphologyEx(blurred_frame, cv2.MORPH_CLOSE, kernel)

        edges = cv2.Canny(blurred_frame, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
        
        if not any(groups[1][1][0] in existing_groups[1][1][0] for existing_groups in face):
            face.append(groups)
            print(f"{groups[1][1][0]} face detected!")
            
    return frame


def color_to_position(color):
    if face[0][1][1][0] == color:
        return "U"
    elif face[1][1][1][0] == color:
        return "R"
    elif face[2][1][1][0] == color:
        return "F"
    elif face[3][1][1][0] == color:
        return "D"
    elif face[4][1][1][0] == color:
        return "L"
    elif face[5][1][1][0] == color:
        return "B"
    return None


def draw_solution(cap, solution):
    global face
    for step in solution:
        if step == "U":
            u_cw(face, cap)
        elif step == "U'":
            u_ccw(face, cap)
        elif step == "R":
            r_cw(face, cap)
        elif step == "R'":
            r_ccw(face, cap)
        elif step == "F":
            f_cw(face, cap)
        elif step == "F'":
            f_ccw(face, cap)
        elif step == "D":
            d_cw(face, cap)
        elif step == "D'":
            d_ccw(face, cap)
        elif step == "L":
            l_cw(face, cap)
        elif step == "L'":
            l_ccw(face, cap)
        elif step == "B":
            b_cw(face, cap)
        elif step == "B'":
            b_ccw(face, cap)


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

        if len(face) < 6:
            cv2.imshow("Rubik\'s Cube Detection", find_face(frame))
        else:
            kociemba_str = ""

            for groups in face:
                print(f"{groups[1][1][0]} face")
                for group in groups:
                    for color, coordinates in group:
                        kociemba_str = kociemba_str + color_to_position(color)
                        print(f"  Color: {color}, Coordinates: {coordinates}")
            
            print(f"\nKociemba String: {kociemba_str}")

            if kociemba_str == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB":
                print("The cube is already solved.")
            else:
                try:
                    solution = kociemba.solve(kociemba_str)
                    print(f"Solution: {solution}")
                    draw_solution(cap, solution.split())
                except Exception as e:
                    print(f"An error occurred while solving the Rubik\'s cube: {e}")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()