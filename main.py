import cv2
import numpy as np
import kociemba
from steps import *

# HSV format
color_ranges = [
    ((0, 100, 100), (4, 255, 255), "Red"),
    ((160, 100, 100), (180, 255, 255), "Red"),
    ((30, 100, 100), (99, 255, 255), "Green"),
    ((100, 100, 100), (130, 255, 255), "Blue"),
    ((21, 100, 100), (35, 255, 255), "Yellow"),
    ((0, 0, 120), (179, 50, 255), "White"),
    ((5, 100, 100), (20, 255, 255), "Orange")
]

colors = []


def is_square(approx): # check if a contour is a square
    if len(approx) == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if aspect_ratio >= 0.95 and aspect_ratio <= 1.05:
            return True
    return False


faces = []
'''
faces = [[[["White",(0,0)],["White",(0,0)],["White",(0,0)]],[["White",(0,0)],["White",(0,0)],["White",(0,0)]],[["White",(0,0)],["White",(0,0)],["White",(0,0)]]],
        [[["Green",(0,0)],["Green",(0,0)],["Green",(0,0)]],[["Green",(0,0)],["Green",(0,0)],["Green",(0,0)]],[["Green",(0,0)],["Blue",(0,0)],["Green",(0,0)]]],
        [[["Orange",(0,0)],["Orange",(0,0)],["Orange",(0,0)]],[["Orange",(0,0)],["Orange",(0,0)],["Orange",(0,0)]],[["Blue",(0,0)],["Orange",(0,0)],["Orange",(0,0)]]],
        [[["Yellow",(0,0)],["Yellow",(0,0)],["Yellow",(0,0)]],[["Yellow",(0,0)],["Yellow",(0,0)],["Yellow",(0,0)]],[["Yellow",(0,0)],["Yellow",(0,0)],["Yellow",(0,0)]]],
        [[["Blue",(0,0)],["Blue",(0,0)],["Blue",(0,0)]],[["Blue",(0,0)],["Blue",(0,0)],["Blue",(0,0)]],[["Orange",(0,0)],["Green",(0,0)],["Red",(0,0)]]],
        [[["Red",(0,0)],["Red",(0,0)],["Red",(0,0)]],[["Red",(0,0)],["Red",(0,0)],["Red",(0,0)]],[["Red",(0,0)],["Red",(0,0)],["Blue",(0,0)]]]
        ]
'''

def white_balancing(frame): # white balancing on the input image frame
    r, g, b = cv2.split(frame)
    
    avg_r = np.mean(r)
    avg_g = np.mean(g)
    avg_b = np.mean(b)
    
    avg_value = (avg_r + avg_g + avg_b) / 3
    
    scale_r = avg_value / avg_r
    scale_g = avg_value / avg_g
    scale_b = avg_value / avg_b
    
    balanced_r = cv2.convertScaleAbs(r, alpha=scale_r, beta=0)
    balanced_g = cv2.convertScaleAbs(g, alpha=scale_g, beta=0)
    balanced_b = cv2.convertScaleAbs(b, alpha=scale_b, beta=0)
    
    result = cv2.merge([balanced_r, balanced_g, balanced_b])
    
    return result


def find_face(frame): # find and highlight the Rubik's cube pieces
    frame = white_balancing(frame)
    lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
    #print(format(lab_frame))
    global faces
    face_colors = []
    groups = []
    squares_found = 0
    
    #result = np.zeros_like(frame)

    for lower_range, upper_range, color_name in colors:
        mask = cv2.inRange(lab_frame, np.array(lower_range), np.array(upper_range))
        #res = cv2.bitwise_and(frame, frame, mask=mask)
        #cv2.imshow(color_name,res)
        #result = cv2.add(result, res)

        blurred_frame = cv2.GaussianBlur(mask, (5, 5), 0)

        kernel = np.ones((5, 5), np.uint8)

        blurred_frame = cv2.morphologyEx(blurred_frame, cv2.MORPH_OPEN, kernel)
        blurred_frame = cv2.morphologyEx(blurred_frame, cv2.MORPH_CLOSE, kernel)

        edges = cv2.Canny(blurred_frame, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #cv2.imshow("Combined Result", result)
        #cv2.drawContours(frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500 and area < 2500:
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
        
        if not any(groups[1][1][0] in existing_groups[1][1][0] for existing_groups in faces):
            faces.append(groups)
            print(f"{groups[1][1][0]} face detected!")
        #else:
            #TODO draw arrows 
            
    return frame


def color_to_position(color):
    if faces[0][1][1][0] == color:
        return "U"
    elif faces[1][1][1][0] == color:
        return "R"
    elif faces[2][1][1][0] == color:
        return "F"
    elif faces[3][1][1][0] == color:
        return "D"
    elif faces[4][1][1][0] == color:
        return "L"
    elif faces[5][1][1][0] == color:
        return "B"
    return None


def draw_solution(cap, solution):
    global faces
    for step in solution:
        if step == "U":
            u_cw(faces, cap)
        elif step == "U'":
            u_ccw(faces, cap)
        elif step == "U2":
            u_cw(faces, cap)
            u_cw(faces, cap)
        elif step == "R":
            r_cw(faces, cap)
        elif step == "R'":
            r_ccw(faces, cap)
        elif step == "R2":
            r_cw(faces, cap)
            r_cw(faces, cap)
        elif step == "F":
            f_cw(faces, cap)
        elif step == "F'":
            f_ccw(faces, cap)
        elif step == "F2":
            f_cw(faces, cap)
            f_cw(faces, cap)
        elif step == "D":
            d_cw(faces, cap)
        elif step == "D'":
            d_ccw(faces, cap)
        elif step == "D2":
            d_cw(faces, cap)
            d_cw(faces, cap)
        elif step == "L":
            l_cw(faces, cap)
        elif step == "L'":
            l_ccw(faces, cap)
        elif step == "L2":
            l_cw(faces, cap)
            l_cw(faces, cap)
        elif step == "B":
            b_cw(faces, cap)
        elif step == "B'":
            b_ccw(faces, cap)
        elif step == "B2":
            b_cw(faces, cap)
            b_cw(faces, cap)


def draw_square(frame, top_left, bottom_right, label):
    cv2.rectangle(frame, top_left, bottom_right, (0, 0, 0), -1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, label, (top_left[0] + 10, bottom_right[1] - 10), font, 1, (255, 255, 255), 2)
    cv2.rectangle(frame, top_left, bottom_right, (255, 255, 255), 2)
    for i in range(1, 3):
        cv2.line(frame, (top_left[0] + i * (bottom_right[0] - top_left[0]) // 3, top_left[1]),
                 (top_left[0] + i * (bottom_right[0] - top_left[0]) // 3, bottom_right[1]), (255, 255, 255), 2)
        cv2.line(frame, (top_left[0], top_left[1] + i * (bottom_right[1] - top_left[1]) // 3),
                 (bottom_right[0], top_left[1] + i * (bottom_right[1] - top_left[1]) // 3), (255, 255, 255), 2)


def draw_cube():
    cube_size = 450
    square_size = cube_size // 3
    frame = np.ones((cube_size, cube_size + square_size, 3), dtype=np.uint8) * 255
    label_positions = {
        'U  0': (square_size * 3 // 2, square_size // 2),
        'L  4': (square_size // 2, square_size * 3 // 2),
        'F  2': (square_size * 3 // 2, square_size * 3 // 2),
        'R  1': (square_size * 5 // 2, square_size * 3 // 2),
        'B  5': (square_size * 7 // 2, square_size * 3 // 2),
        'D  3': (square_size * 3 // 2, square_size * 5 // 2)
    }
    for label, position in label_positions.items():
        top_left = (position[0] - square_size // 2, position[1] - square_size // 2)
        bottom_right = (position[0] + square_size // 2, position[1] + square_size // 2)
        draw_square(frame, top_left, bottom_right, label)
    cv2.imshow("Open Cube", frame)


color_names = ["Red", "Green", "Blue", "Yellow", "White", "Orange"]
click_count = 0
def showPixelValue(event,x,y,flags,param): # handle mouse click events for color selection
    global frame, colors, click_count

    frame_height, frame_width = frame.shape[:2]

    if x > frame_width - 1 or y > frame_height - 1: return
    if event == cv2.EVENT_LBUTTONDOWN:
        bgr = frame[y, x]
        lab = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2LAB)[0][0]
        print(lab)
        if click_count == 0: # Red
            l_threshold, a_threshold, b_threshold = 25, 20, 20
        elif click_count == 1: # Green
            l_threshold, a_threshold, b_threshold = 25, 20, 20
        elif click_count == 2: # Blue
            l_threshold, a_threshold, b_threshold = 25, 20, 20
        elif click_count == 3: # Yellow
            l_threshold, a_threshold, b_threshold = 25, 20, 20
        elif click_count == 4: # White
            l_threshold, a_threshold, b_threshold = 25, 20, 20
        else: # Orange
             l_threshold, a_threshold, b_threshold = 25, 20, 20
        colors.append((
            (max(0, lab[0] - l_threshold), max(0, lab[1] - a_threshold), max(0, lab[2] - b_threshold)),
            (min(255, lab[0] + l_threshold), min(255, lab[1] + a_threshold), min(255, lab[2] + b_threshold)),
            color_names[click_count]
        ))
        click_count += 1
    cv2.imshow("Rubik\'s Cube Detection", frame)

def dummy_callback(event, x, y, flags, param):
    pass

def main():
    global frame
    cap = cv2.VideoCapture(0) # initialize the camera

    if not cap.isOpened():
        print("Can\'t capture camera")
        exit()


    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can\'t receive frame")
            break
        
        if click_count >= 6: 
            cv2.setMouseCallback("Rubik\'s Cube Detection", dummy_callback)
            break
        else:
            frame = white_balancing(frame)
            cv2.namedWindow("Rubik\'s Cube Detection")
            cv2.setMouseCallback("Rubik\'s Cube Detection", showPixelValue)
            cv2.putText(frame, f"Click on a {color_names[click_count]} piece with your mouse", (60,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2)
            #cv2.imshow("Rubik\'s Cube Detection", find_face(frame))
            cv2.imshow("Rubik\'s Cube Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can\'t receive frame")
            break

        draw_cube()

        if len(faces) < 6:
            cv2.imshow("Rubik\'s Cube Detection", find_face(frame))
        else:
            kociemba_str = ""

            for groups in faces:
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