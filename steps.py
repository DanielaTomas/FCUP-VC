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


def compare_faces(face1, face2):
    for i in range(3):
        for j in range(3):
            color1, _ = face1[i][j]
            color2, _ = face2[i][j]
            
            if color1 != color2:
                return False
    return True


def draw_arrow(frame, start, end, color, arrow_thickness):
    cv2.arrowedLine(frame, start, end, color, arrow_thickness, tipLength=0.2)


def x_arrows(frame, current_face, var, arrow_length, arrow_color, arrow_thickness):
    x_start, y_start = current_face[0][1][1][0] - var, current_face[0][1][1][1] + var
    x_end, y_end = x_start + arrow_length, y_start
    draw_arrow(frame, (x_end, y_start), (x_start, y_end), arrow_color, arrow_thickness)
    x_start, y_start = current_face[1][1][1][0] - var, current_face[1][1][1][1] + var
    x_end, y_end = x_start + arrow_length, y_start
    draw_arrow(frame, (x_end, y_start), (x_start, y_end), arrow_color, arrow_thickness)
    x_start, y_start = current_face[2][1][1][0] - var, current_face[2][1][1][1] + var
    x_end, y_end = x_start + arrow_length, y_start
    draw_arrow(frame, (x_end, y_start), (x_start, y_end), arrow_color, arrow_thickness)


def f_b_arrows(frame, current_face, var, arrow_length, arrow_color, arrow_thickness, step):
        arrow_length -= 50
        x_start, y_start = current_face[0][1][1][0] + var, current_face[1][2][1][1]
        x_end, y_end = x_start + arrow_length, y_start - arrow_length
        draw_arrow(frame, (x_start, y_end) if step == "F" or step == "B" else (x_end, y_start), (x_end, y_start) if step == "F" or step == "B"  else (x_start, y_end), arrow_color, arrow_thickness)
        x_start -= var
        x_end = x_start - arrow_length
        draw_arrow(frame, (x_end, y_start) if step == "F" or step == "B"  else (x_start, y_end), (x_start, y_end) if step == "F" or step == "B"  else (x_end, y_start), arrow_color, arrow_thickness)
        y_start += var
        y_end = y_start + arrow_length
        draw_arrow(frame, (x_start, y_end) if step == "F" or step == "B"  else (x_end, y_start), (x_end, y_start) if step == "F" or step == "B"  else (x_start, y_end), arrow_color, arrow_thickness)
        x_start += var
        x_end = x_start + arrow_length
        draw_arrow(frame, (x_end, y_start) if step == "F" or step == "B"  else (x_start, y_end), (x_start, y_end) if step == "F" or step == "B"  else (x_end, y_start), arrow_color, arrow_thickness)


def draw_arrows(current_face, b_face, frame, step):
    arrow_length = 100
    arrow_thickness = 4
    arrow_color = (0, 0, 255)
    var = 25

    if(step == "U" or step == "U'"):
        x_start, y_start = current_face[0][1][1][0] - var, current_face[0][1][1][1] + var
        x_end, y_end = x_start + arrow_length, y_start
        draw_arrow(frame, (x_end, y_start) if step == "U" else (x_start, y_start), (x_start, y_end) if step == "U" else (x_end, y_end), arrow_color, arrow_thickness)

    elif(step == "R" or step == "R'"):
        x_start, y_start = current_face[2][2][1][0] + var, current_face[2][2][1][1]
        x_end, y_end = x_start, y_start - arrow_length
        draw_arrow(frame, (x_start, y_start) if step == "R" else (x_start, y_end), (x_end, y_end) if step == "R" else (x_end, y_start), arrow_color, arrow_thickness)

    elif(step == "F" or step == "F'"):
        f_b_arrows(frame, current_face, var, arrow_length, arrow_color, arrow_thickness, step)

    elif(step == "D" or step == "D'"):
        x_start, y_start = current_face[2][1][1][0] - var, current_face[2][1][1][1] + var
        x_end, y_end = x_start + arrow_length, y_start
        draw_arrow(frame, (x_end, y_start) if step == "D'" else (x_start, y_start), (x_start, y_end) if step == "D'" else (x_end, y_end), arrow_color, arrow_thickness)

    elif(step == "L" or step == "L'"):
        x_start, y_start = current_face[2][0][1][0] + var, current_face[2][0][1][1]
        x_end, y_end = x_start, y_start - arrow_length
        draw_arrow(frame, (x_start, y_start) if step == "L'" else (x_start, y_end), (x_end, y_end) if step == "L'" else (x_end, y_start), arrow_color, arrow_thickness)

    elif(step == "B" or step == "B'"):
        if not compare_faces(current_face, b_face):
            x_arrows(frame, current_face, var, arrow_length, arrow_color, arrow_thickness)
        else:
            f_b_arrows(frame, current_face, var, arrow_length, arrow_color, arrow_thickness, step)

    else:
        x_arrows(frame, current_face, var, arrow_length, arrow_color, arrow_thickness)

      
def process_frame(faces, cap, step):
    #TODO Apagar isto depois ---- debug
    for groups in faces:
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
                #TODO testar melhor
                if step == 'B' or step == 'B\'':
                    if compare_faces(current_face,faces[5]):
                        draw_arrows(current_face, faces, frame_with_cube, 'y')
                        cv2.imshow("Rubik\'s Cube Detection", frame_with_cube)
                    else:
                        draw_arrows(current_face, faces[5], frame_with_cube, step)
                        cv2.imshow("Rubik\'s Cube Detection", frame_with_cube)
                else:
                    if compare_faces(current_face, faces[2]):
                        break
                    else:
                        draw_arrows(current_face, faces[5], frame_with_cube, step)
                        cv2.imshow("Rubik\'s Cube Detection", frame_with_cube)
                

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                exit()


def rotate_cw(faces, temp, n):
    faces[n][0][0] = temp[n][2][0]
    faces[n][0][1] = temp[n][1][0]
    faces[n][0][2] = temp[n][0][0]

    faces[n][1][0] = temp[n][2][1]
    faces[n][1][2] = temp[n][0][1]
    faces[n][2][2] = temp[n][0][2]

    faces[n][2][0] = temp[n][2][2]
    faces[n][2][1] = temp[n][1][2]


def rotate_ccw(faces, temp, n):
    faces[n][0][0] = temp[n][0][2]
    faces[n][0][1] = temp[n][1][2]
    faces[n][0][2] = temp[n][2][2]

    faces[n][1][0] = temp[n][0][1]
    faces[n][1][2] = temp[n][2][1]
    faces[n][2][2] = temp[n][2][0]

    faces[n][2][0] = temp[n][0][0]
    faces[n][2][1] = temp[n][1][0]


def u_cw(faces, cap): # rotate the upper face clockwise
    print('Rotate: U')
    temp = copy.deepcopy(faces)

    rotate_cw(faces, temp, 0)

    for i in range(3):
        faces[4][0][i] = temp[2][0][i]
        faces[5][0][i] = temp[4][0][i]
        faces[1][0][i] = temp[5][0][i]
        faces[2][0][i] = temp[1][0][i]

    process_frame(faces, cap, "U")            


def u_ccw(faces, cap): # rotate the upper face counter-clockwise
    print('Rotate: U\'')
    temp = copy.deepcopy(faces)
    
    rotate_ccw(faces, temp, 0)

    for i in range(3):
        faces[1][0][i] = temp[2][0][i]
        faces[5][0][i] = temp[1][0][i]
        faces[4][0][i] = temp[5][0][i]
        faces[2][0][i] = temp[4][0][i]

    process_frame(faces, cap, "U'")


def r_cw(faces, cap): # rotate the right face clockwise
    print('Rotate: R')
    temp = copy.deepcopy(faces)

    rotate_cw(faces, temp, 1)

    for i in range(3):
        faces[0][i][2] = temp[2][i][2]
        faces[5][2-i][0] = temp[0][i][2]
        faces[3][i][2] = temp[5][2-i][0]
        faces[2][i][2] = temp[3][i][2]
    
    process_frame(faces, cap, "R")


def r_ccw(faces, cap): # rotate the right face counter-clockwise
    print('Rotate: R\'')
    temp = copy.deepcopy(faces)

    rotate_ccw(faces, temp, 1)

    for i in range(3):
        faces[2][i][2] = temp[0][i][2]
        faces[0][i][2] = temp[5][2-i][0]
        faces[5][2-i][0] = temp[3][i][2]
        faces[3][i][2] = temp[2][i][2]

    process_frame(faces, cap, "R'")


def f_cw(faces, cap): # rotate the front face clockwise
    print('Rotate: F')
    temp = copy.deepcopy(faces)

    rotate_cw(faces, temp, 2)

    for i in range(3):
        faces[1][i][0] = temp[0][2][i]
        faces[3][0][i] = temp[1][2-i][0]
        faces[4][i][2] = temp[3][0][i]
        faces[0][2][2-i] = temp[4][i][2]
     
    process_frame(faces, cap, "F")


def f_ccw(faces, cap): # rotate the front face counter-clockwise
    print('Rotate: F\'')
    temp = copy.deepcopy(faces)

    rotate_ccw(faces, temp, 2)

    for i in range(3):
        faces[4][i][2] = temp[0][2][2-i]
        faces[3][0][i] = temp[4][i][2]
        faces[1][2-i][0] = temp[3][0][i]
        faces[0][2][i] = temp[1][i][0]
    
    process_frame(faces, cap, "F'")


def d_cw(faces, cap): # rotate the front face clockwise
    print('Rotate: D')
    temp = copy.deepcopy(faces)

    rotate_cw(faces, temp, 3)

    for i in range(3):
        faces[1][2][i] = temp[2][2][i]
        faces[5][2][i] = temp[1][2][i]
        faces[4][2][i] = temp[5][2][i]
        faces[2][2][i] = temp[4][2][i]
    
    process_frame(faces, cap, "D")


def d_ccw(faces, cap): # rotate the front face counter-clockwise
    print('Rotate: D\'')
    temp = copy.deepcopy(faces)

    rotate_ccw(faces, temp, 3)

    for i in range(3):
        faces[1][2][i] = temp[5][2][i]
        faces[5][2][i] = temp[4][2][i]
        faces[4][2][i] = temp[2][2][i]
        faces[2][2][i] = temp[1][2][i]

    process_frame(faces, cap, "D'")


def l_cw(faces, cap): # rotate the left face clockwise
    print('Rotate: L')
    temp = copy.deepcopy(faces)
    
    rotate_cw(faces, temp, 4)

    for i in range(3):
        faces[0][i][0] = temp[5][2-i][2]
        faces[2][i][0] = temp[0][i][0]
        faces[3][i][0] = temp[2][i][0]
        faces[5][2-i][2] = temp[3][i][0] 

    process_frame(faces, cap, "L") 


def l_ccw(faces, cap): # rotate the left face counter-clockwise
    print('Rotate: L\'')
    temp = copy.deepcopy(faces)
    
    rotate_ccw(faces, temp, 4)

    for i in range(3):
        faces[0][i][0] = temp[2][i][0]
        faces[5][2-i][2] = temp[0][i][0]
        faces[3][i][0] = temp[5][2-i][2]
        faces[2][i][0] = temp[3][i][0]

    process_frame(faces, cap, "L'") 


def b_cw(faces, cap): # rotate the back face clockwise
    print('Rotate: B')
    temp = copy.deepcopy(faces)

    rotate_cw(faces, temp, 5)

    for i in range(3):
        faces[4][i][0] = temp[0][0][2-i]
        faces[3][2][i] = temp[4][i][0]
        faces[1][2-i][2] = temp[3][2][i]
        faces[0][0][i] = temp[1][i][2] 

    process_frame(faces, cap, "B") 


def b_ccw(faces, cap): # rotate the right face counter-clockwise
    print('Rotate: B\'')
    temp = copy.deepcopy(faces)
    
    rotate_ccw(faces, temp, 5)

    for i in range(3):
        faces[1][i][2] = temp[0][0][i]
        faces[3][2][i] = temp[1][2-i][2]
        faces[4][i][0] = temp[3][2][i]
        faces[0][0][2-i] = temp[4][i][0] 

    process_frame(faces, cap, "B'") 