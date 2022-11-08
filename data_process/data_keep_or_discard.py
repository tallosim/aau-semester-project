import cv2 as cv
import glob
import os


RADIUS = 3


def load_data(folder_path):
    image_paths = glob.glob(os.path.join(folder_path, 'images', 'train', '*.jpg'))
    label_paths = glob.glob(os.path.join(folder_path, 'labels', 'train', '*.txt'))
    
    image_paths = list(sorted(image_paths))
    label_paths = list(sorted(label_paths))
    
    classes = open(os.path.join(folder_path, 'classes.txt'), 'r').read().splitlines()

    print("Received folder path:",folder_path)
    print(len(image_paths),"Image path:",image_paths)
    print(len(label_paths),"Label path:",label_paths)
    print("")
    return image_paths, label_paths, classes


def show_image(image_path, label_path, classes, colors):
    global image_with_bounding

    image = cv.imread(image_path)
    print("Received image path:",image_path)

    bounding_boxes_read = open(label_path, 'r').read().splitlines()
    image_with_bounding = image.copy()

    for line in bounding_boxes_read:
        type, x, y, w, h = line.split(' ')
        x, y, w, h = float(x), float(y), float(w), float(h)
        print("Label data:", type, x, y, w, h)
        print("")

        color = colors[int(type)]
        class_name = classes[int(type)]

        pixel_x = int(x * image.shape[1])
        pixel_y = int(y * image.shape[0])
        pixel_width = int(w * image.shape[1])
        pixel_height = int(h * image.shape[0])

        pixel_x = pixel_x - int(pixel_width / 2)
        pixel_y = pixel_y - int(pixel_height / 2)
        
        p1 = (pixel_x, pixel_y)
        p2 = (pixel_x + pixel_width, pixel_y)
        p3 = (pixel_x + pixel_width, pixel_y + pixel_height)
        p4 = (pixel_x, pixel_y + pixel_height)

        cv.rectangle(image_with_bounding, (p1[0]-RADIUS, p1[1]-RADIUS), (p1[0]+RADIUS, p1[1]+RADIUS), color, -1)
        cv.rectangle(image_with_bounding, (p2[0]-RADIUS, p2[1]-RADIUS), (p2[0]+RADIUS, p2[1]+RADIUS), color, -1)
        cv.rectangle(image_with_bounding, (p3[0]-RADIUS, p3[1]-RADIUS), (p3[0]+RADIUS, p3[1]+RADIUS), color, -1)
        cv.rectangle(image_with_bounding, (p4[0]-RADIUS, p4[1]-RADIUS), (p4[0]+RADIUS, p4[1]+RADIUS), color, -1)

        cv.rectangle(image_with_bounding, (pixel_x, pixel_y), (pixel_x + pixel_width, pixel_y + pixel_height), color, 2)
        cv.putText(image_with_bounding, class_name, (pixel_x, pixel_y - 12), 0, 0.8, color, 2)

    initial_coordinate = 0,0
    final_coordinate = 0,0

    while True:
        cv.imshow("Image", image_with_bounding)
        cv.setMouseCallback('Image', mouse_event)

        key_press = cv.waitKey(1)
        if key_press != -1:
            print("Key press:",key_press)

        # Based on the OpenCV grabcut example: https://github.com/opencv/opencv/blob/master/samples/python/grabcut.py
        if key_press == ord('q'):
            break

        elif key_press == ord('1'):
            roi_selected = cv.selectROI('Image', image_with_bounding)
            print("ROI Selected:",roi_selected)
            pass

        elif key_press == ord('2'):
            pass

        elif key_press == (8 or 46):
            print('Deleting bounding box at coordinate:',mouse_position_x,mouse_position_y)

        # If key-press is backspace or delete
        elif key_press == 27:
            return True


mouse_left_pressed = False
mouse_right_pressed = False
mouse_position_x = 0
mouse_position_y = 0


def mouse_event(event, x, y,_,__):
    global mouse_left_pressed
    global mouse_right_pressed
    global mouse_position_x
    global mouse_position_y

    mouse_position_x = x
    mouse_position_y = y

    # print("Event:", event, 'X:',x,'Y:',y)

    # Left-mouse down
    if event == 1:
        print("Mouse-left pressed",'X:',x,'Y:',y)
        mouse_left_pressed = True

    # Right-mouse down
    if event == 2:
        print("Right-left pressed",'X:',x,'Y:',y)
        mouse_right_pressed = True

    # Left-mouse down
    if event == 4:
        print("Mouse-left released",'X:',x,'Y:',y)
        mouse_left_pressed = False

    # Right-mouse down
    if event == 5:
        print("Right-left released",'X:',x,'Y:',y)
        mouse_right_pressed = False


def conver_hex_to_decimal_color(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))
    

if __name__ == '__main__':
    yolo_folder_path = input('Insert folder path to YOLO:\n')

    # Short-cut
    if yolo_folder_path == "L":
        yolo_folder_path = r'C:\Users\lukad\Desktop\Computer Vision 7th semester project COM_ENG\yolo'

    image_paths, label_paths, classes = load_data(yolo_folder_path)
    
    colors = ['#d22b2b', '#389e0d', '#ffc069', '#ad8b00', '#1759ab']
    colors = [conver_hex_to_decimal_color(color) for color in colors]

    for i in range(len(image_paths)):
        if_close = show_image(image_paths[i], label_paths[i], classes, colors)

        if if_close:
            break