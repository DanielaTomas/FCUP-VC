import cv2
import numpy as np
from main import is_square, color_ranges
import copy

def find_face(frame): #TODO tirar daqui e juntar com a do main
    
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
        
        print(f"{groups[1][1][0]} face detected!")
        
    return frame, groups


def rotate_cw(face, temp, n):
    face[n][0][0] = temp[n][2][0]
    face[n][0][1] = temp[n][1][0]
    face[n][0][2] = temp[n][0][0]

    face[n][1][0] = temp[n][2][1]
    face[n][1][2] = temp[n][0][1]
    face[n][2][2] = temp[n][0][2]

    face[n][2][0] = temp[n][2][2]
    face[n][2][1] = temp[n][1][2]


def rotate_ccw(face, temp, n):
    face[n][0][0] = temp[n][0][2]
    face[n][0][1] = temp[n][1][2]
    face[n][0][2] = temp[n][2][2]

    face[n][1][0] = temp[n][0][1]
    face[n][1][2] = temp[n][2][1]
    face[n][2][2] = temp[n][2][0]

    face[n][2][0] = temp[n][0][0]
    face[n][2][1] = temp[n][1][0]


def compare_faces(face1, face2):
    for i in range(3):
        for j in range(3):
            color1, _ = face1[i][j]
            color2, _ = face2[i][j]
            
            if color1 != color2:
                return False
    return True


def process_frame(face, cap, step):
    #TODO Apagar isto depois ---- debug
    for groups in face:
        print(f"{groups[1][1][0]} face")
        for group in groups:
            for color, coordinates in group:
                print(f"  Color: {color}, Coordinates: {coordinates}")
    #----
    while True:
            ret, frame = cap.read()

            if not ret:
                print("Can\'t receive frame")
                exit()

            frame_with_cube, current_face = find_face(frame)
            cv2.imshow("Rubik\'s Cube Detection", frame_with_cube)

            if current_face != []:
                if compare_faces(current_face,face[2]):
                    break
                else:
                    print(step)
                    print('draw arrows')
                    #TODO draw arrows

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                exit()


def u_cw(face, cap): # rotate the upper face clockwise
    temp = copy.deepcopy(face)

    rotate_cw(face, temp, 0)

    for i in range(3):
        face[4][0][i] = temp[2][0][i]
        face[5][0][i] = temp[4][0][i]
        face[1][0][i] = temp[5][0][i]
        face[2][0][i] = temp[1][0][i]

    process_frame(face, cap, "U")            


def u_ccw(face, cap): # rotate the upper face counter-clockwise
    temp = copy.deepcopy(face)
    
    rotate_ccw(face, temp, 0)

    for i in range(3):
        face[1][0][i] = temp[2][0][i]
        face[5][0][i] = temp[1][0][i]
        face[4][0][i] = temp[5][0][i]
        face[2][0][i] = temp[4][0][i]

    process_frame(face, cap, "U'")


def r_cw(face, cap): # rotate the right face clockwise
    temp = copy.deepcopy(face)

    rotate_cw(face, temp, 1)

    for i in range(3):
        face[0][i][2] = temp[2][i][2]
        face[5][2-i][0] = temp[0][i][2]
        face[3][i][2] = temp[5][2-i][0]
        face[2][i][2] = temp[3][i][2]
    
    process_frame(face, cap, "R")


def r_ccw(face, cap): # rotate the right face counter-clockwise
    temp = copy.deepcopy(face)

    rotate_ccw(face, temp, 1)

    for i in range(3):
        face[2][i][2] = temp[0][i][2]
        face[0][i][2] = temp[5][2-i][0]
        face[5][2-i][0] = temp[3][i][2]
        face[3][i][2] = temp[2][i][2]

    process_frame(face, cap, "R'")


def f_cw(face, cap): # rotate the front face clockwise
    temp = copy.deepcopy(face)

    rotate_cw(face, temp, 2)

    for i in range(3):
        face[1][i][0] = temp[0][2][i]
        face[3][0][i] = temp[1][2-i][0]
        face[4][i][2] = temp[3][0][i]
        face[0][2][2-i] = temp[4][i][2]
     
    process_frame(face, cap, "F")


def f_ccw(face, cap): # rotate the front face counter-clockwise
    temp = copy.deepcopy(face)

    rotate_ccw(face, temp, 2)

    for i in range(3):
        face[4][i][2] = temp[0][2][2-i]
        face[3][0][i] = temp[4][i][2]
        face[1][2-i][0] = temp[3][0][i]
        face[0][2][i] = temp[1][i][0]
    
    process_frame(face, cap, "F'")


def d_cw(face, cap): # rotate the front face clockwise
    temp = copy.deepcopy(face)

    rotate_cw(face, temp, 3)

    for i in range(3):
        face[1][2][i] = temp[2][2][i]
        face[5][2][i] = temp[1][2][i]
        face[4][2][i] = temp[5][2][i]
        face[2][2][i] = temp[4][2][i]
    
    process_frame(face, cap, "D")


def d_ccw(face, cap): # rotate the front face counter-clockwise
    temp = copy.deepcopy(face)

    rotate_ccw(face, temp, 3)

    for i in range(3):
        face[1][2][i] = temp[5][2][i]
        face[5][2][i] = temp[4][2][i]
        face[4][2][i] = temp[2][2][i]
        face[2][2][i] = temp[1][2][i]

    process_frame(face, cap, "D'")


def l_cw(face, cap): # rotate the left face clockwise
    temp = copy.deepcopy(face)
    
    rotate_cw(face, temp, 4)

    for i in range(3):
        face[0][i][0] = temp[5][2-i][2]
        face[2][i][0] = temp[0][i][0]
        face[3][i][0] = temp[2][i][0]
        face[5][2-i][2] = temp[3][i][0] 

    process_frame(face, cap, "L") 


def l_ccw(face, cap): # rotate the left face counter-clockwise
    temp = copy.deepcopy(face)
    
    rotate_ccw(face, temp, 4)

    for i in range(3):
        face[0][i][0] = temp[2][i][0]
        face[5][2-i][2] = temp[0][i][0]
        face[3][i][0] = temp[5][2-i][2]
        face[2][i][0] = temp[3][i][0]

    process_frame(face, cap, "L'") 


def b_cw(face, cap): # rotate the back face clockwise
    temp = copy.deepcopy(face)

    rotate_cw(face, temp, 5)

    for i in range(3):
        face[4][i][0] = temp[0][0][2-i]
        face[3][2][i] = temp[4][i][0]
        face[1][2-i][2] = temp[3][2][i]
        face[0][0][i] = temp[1][i][2] 

    process_frame(face, cap, "B") 


def b_ccw(face, cap): # rotate the right face counter-clockwise
    temp = copy.deepcopy(face)
    
    rotate_ccw(face, temp, 5)

    for i in range(3):
        face[1][i][2] = temp[0][0][i]
        face[3][2][i] = temp[1][2-i][2]
        face[4][i][0] = temp[3][2][i]
        face[0][0][2-i] = temp[4][i][0] 

    process_frame(face, cap, "B'") 