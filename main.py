import cv2
import numpy as np
import kociemba

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
    global face
    face_colors = []
    groups = []
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
        
        if not any(groups[1][1][0] in existing_groups[1][1][0] for existing_groups in face):
            face.append(groups)
            #cv2.imwrite(f"frame{groups[1][1][0]}.jpg", frame)
            print(f"{groups[1][1][0]} face detected!")


    #draw_arrows(frame, groups)
            
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


'''
def draw_arrows(frame, groups):
    arrow_length = 80
    arrow_color = (0, 0, 255)
    arrow_thickness = 4
    
    for group in groups:
        x_center = group[1][1][0]  # x-coordinate of the center square

        # draw an arrow pointing to the right
        start_point = (x_center - 20, group[1][1][1] + 20)
        end_point = (x_center + arrow_length, group[1][1][1] + 20)
        cv2.arrowedLine(frame, start_point, end_point, arrow_color, arrow_thickness)
'''


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

        frame_with_cube = find_rubiks_cube(frame) #if len(face) == 6

        cv2.imshow("Rubik\'s Cube Detection", frame_with_cube)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    kociemba_str = ""
    # print
    for groups in face:
        print(f"{groups[1][1][0]} face")
        for group in groups:
            for color, coordinates in group:
                kociemba_str = kociemba_str + color_to_position(color)
                print(f"  Color: {color}, Coordinates: {coordinates}")
    
    print(f"\nKociemba String: {kociemba_str}")

    print(f"Solution: {kociemba.solve(kociemba_str)}")

if __name__ == "__main__":
    main()