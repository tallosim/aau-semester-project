import cv2 as cv
import glob
import os

RADIUS = 8


class ImageWindow:
    def __init__(self, image_path, label_path, classes, colors):
        self.classes = classes
        self.colors = colors
        self.label_path = label_path
        self.file_name = os.path.basename(image_path)
        self.changed = False
        
        self.move_point = None
        self.last_selected_object = None
        
        self.image = cv.imread(image_path)
        
        labels = open(label_path, 'r').read().splitlines()
        self.labels = dict()
        
        for index, line in enumerate(labels):
            type, x, y, w, h = line.split(' ')
            x, y, w, h = float(x), float(y), float(w), float(h)

            pixel_x = int(x * self.image.shape[1])
            pixel_y = int(y * self.image.shape[0])
            pixel_width = int(w * self.image.shape[1])
            pixel_height = int(h * self.image.shape[0])

            pixel_x = pixel_x - int(pixel_width / 2)
            pixel_y = pixel_y - int(pixel_height / 2)
            
            self.labels[index] = {
                'type': type, 
                'pixel_x': pixel_x,
                'pixel_y': pixel_y,
                'pixel_width': pixel_width,
                'pixel_height': pixel_height
                }
    
    def save_labels(self):
        if self.changed:
            print('Saving labels...')
            print(self.label_path)
            with open(self.label_path, 'w') as file:
                for key in self.labels.keys():
                    label = self.labels[key]
                    type = label['type']
                    x = (label['pixel_x'] + int(label['pixel_width'] / 2)) / self.image.shape[1]
                    y = (label['pixel_y'] + int(label['pixel_height'] / 2)) / self.image.shape[0]
                    w = label['pixel_width'] / self.image.shape[1]
                    h = label['pixel_height'] / self.image.shape[0]
                    file.write(f'{type} {x} {y} {w} {h}\n')
                    
    
    def calc_points(self, label):
        p1 = (label['pixel_x'], label['pixel_y'])
        p2 = (label['pixel_x'] + label['pixel_width'], label['pixel_y'])
        p3 = (label['pixel_x'] + label['pixel_width'], label['pixel_y'] + label['pixel_height'])
        p4 = (label['pixel_x'], label['pixel_y'] + label['pixel_height'])
        return p1, p2, p3, p4
    
    def draw_bounding_box(self):
        image_draw = self.image.copy()
        
        cv.putText(image_draw, self.file_name, (10, 30), 0, 1, (0, 0, 255), 2)
        
        for key in self.labels.keys():
            label = self.labels[key]
            type = label['type']
            
            color = colors[int(type)]
            class_name = classes[int(type)]
            
            p1, p2, p3, p4 = self.calc_points(label)

            cv.rectangle(image_draw, (p1[0]-RADIUS, p1[1]-RADIUS), (p1[0]+RADIUS, p1[1]+RADIUS), color, -1)
            cv.rectangle(image_draw, (p2[0]-RADIUS, p2[1]-RADIUS), (p2[0]+RADIUS, p2[1]+RADIUS), color, -1)
            cv.rectangle(image_draw, (p3[0]-RADIUS, p3[1]-RADIUS), (p3[0]+RADIUS, p3[1]+RADIUS), color, -1)
            cv.rectangle(image_draw, (p4[0]-RADIUS, p4[1]-RADIUS), (p4[0]+RADIUS, p4[1]+RADIUS), color, -1)

            cv.rectangle(image_draw, p1, p3, color, 2)
            cv.putText(image_draw, class_name, (p1[0], p1[1] - 12), 0, 0.8, color, 2)
        
        return image_draw
    
    def show_image(self):
        image_draw = self.draw_bounding_box()
        
        cv.resizeWindow('Image', min(1280, image_draw.shape[1]), min(720, image_draw.shape[0]))     
        cv.imshow('Image', image_draw)
        cv.setMouseCallback('Image', self.mouse_callback)
        while True:
            image_draw = self.draw_bounding_box()   
            cv.imshow('Image', image_draw)
            
            key = cv.waitKey(10)
            
            if key == ord('q'):
                self.save_labels()
                return 0
            
            # D or right arrow or space
            elif key == ord(' ') or key == ord('d') or key == 124:
                self.save_labels()
                return 1
            
            # A or left arrow
            elif key == ord('a') or key == 123:
                self.save_labels()
                return -1
            
            # Delete or Backspace
            elif (key == 46 or key == 8 ) and self.move_point is not None and self.move_point[1] == 'object':
                self.changed = True
                del self.labels[self.move_point[0]]
            
            # Between 0 and 9
            elif key <= 57 and key >= 48 and len(self.classes) > key - 48:
                if self.move_point is not None and self.move_point[1] == 'object':
                    self.changed = True
                    self.labels[self.move_point[0]]['type'] = str(key - 48)
                
                elif self.last_selected_object is not None:
                    self.changed = True
                    self.labels[self.last_selected_object]['type'] = str(key - 48)
                    
        
            
    def mouse_callback(self, action, x, y, flags, userdata):
        if action == cv.EVENT_LBUTTONUP and self.move_point:
            self.last_selected_object = self.move_point[0]
            self.move_point = None
            
        elif action == cv.EVENT_MOUSEMOVE and self.move_point:
            if self.move_point[1] == 'p1':
                self.labels[self.move_point[0]]['pixel_width'] = self.labels[self.move_point[0]]['pixel_width'] + self.labels[self.move_point[0]]['pixel_x'] - x
                self.labels[self.move_point[0]]['pixel_height'] = self.labels[self.move_point[0]]['pixel_height'] + self.labels[self.move_point[0]]['pixel_y'] - y
                self.labels[self.move_point[0]]['pixel_x'] = x
                self.labels[self.move_point[0]]['pixel_y'] = y
                
            elif self.move_point[1] == 'p2':
                self.labels[self.move_point[0]]['pixel_width'] = x - self.labels[self.move_point[0]]['pixel_x']
                self.labels[self.move_point[0]]['pixel_height'] = self.labels[self.move_point[0]]['pixel_height'] + self.labels[self.move_point[0]]['pixel_y'] - y
                self.labels[self.move_point[0]]['pixel_x'] = x - self.labels[self.move_point[0]]['pixel_width']
                self.labels[self.move_point[0]]['pixel_y'] = y
                
            elif self.move_point[1] == 'p3':
                self.labels[self.move_point[0]]['pixel_width'] = x - self.labels[self.move_point[0]]['pixel_x']
                self.labels[self.move_point[0]]['pixel_height'] = y - self.labels[self.move_point[0]]['pixel_y']
                self.labels[self.move_point[0]]['pixel_x'] = x - self.labels[self.move_point[0]]['pixel_width']
                self.labels[self.move_point[0]]['pixel_y'] = y - self.labels[self.move_point[0]]['pixel_height']
                
            elif self.move_point[1] == 'p4':
                self.labels[self.move_point[0]]['pixel_width'] = self.labels[self.move_point[0]]['pixel_width'] + self.labels[self.move_point[0]]['pixel_x'] - x
                self.labels[self.move_point[0]]['pixel_height'] = y - self.labels[self.move_point[0]]['pixel_y']
                self.labels[self.move_point[0]]['pixel_x'] = x
                self.labels[self.move_point[0]]['pixel_y'] = y - self.labels[self.move_point[0]]['pixel_height']
                
            elif self.move_point[1] == 'object':
                if self.move_point[0] in self.labels:
                    self.labels[self.move_point[0]]['pixel_x'] = x - self.move_point[2][0]
                    self.labels[self.move_point[0]]['pixel_y'] = y - self.move_point[2][1]

            
            if self.labels[self.move_point[0]]['pixel_width'] < 10:
                self.labels[self.move_point[0]]['pixel_width'] = 10
                
            if self.labels[self.move_point[0]]['pixel_height'] < 10:
                self.labels[self.move_point[0]]['pixel_height'] = 10
        
        elif action == cv.EVENT_LBUTTONDOWN:
            for label_index in self.labels.keys():
                label = self.labels[label_index]
                
                for index, key in enumerate(['p1', 'p2', 'p3', 'p4']):
                    point = self.calc_points(label)[index]
                    if abs(point[0] - x) <= RADIUS and abs(point[1] - y) <= RADIUS:
                        self.changed = True
                        self.move_point = (label_index, key)
                        
                if x >= label['pixel_x'] + RADIUS and x <= label['pixel_x'] + label['pixel_width'] - RADIUS and \
                    y >= label['pixel_y'] + RADIUS and y <= label['pixel_y'] + label['pixel_height'] - RADIUS:
                    offset = (x - label['pixel_x'], y - label['pixel_y'])
                    self.changed = True
                    self.move_point = (label_index, 'object', offset)
        
        elif action == cv.EVENT_RBUTTONDOWN:
            self.changed = True
            self.labels[str(len(self.labels))] = {
                'pixel_x': x,
                'pixel_y': y,
                'pixel_width': 10,
                'pixel_height': 10,
                'type': 0
            }
            self.move_point = (str(len(self.labels) - 1), 'p3')
            
        elif action == cv.EVENT_RBUTTONUP and self.move_point:
            self.last_selected_object = self.move_point[0]
            self.move_point = None
                        


def load_data(folder_path):
    image_paths = []
    label_paths = []
    
    for path in ['train', 'test', 'valid']:
        image_paths += glob.glob(os.path.join(folder_path, 'images', path, '*.jpg'))
        label_paths += glob.glob(os.path.join(folder_path, 'labels', path, '*.txt'))

    image_paths = list(sorted(image_paths))
    label_paths = list(sorted(label_paths))
    
    classes = open(os.path.join(folder_path, 'classes.txt'), 'r').read().splitlines()

    print('Received folder path:',folder_path)
    return image_paths, label_paths, classes


def conver_hex_to_decimal_color(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))
    

if __name__ == '__main__':
    yolo_folder_path = input('Insert folder path to YOLO:\n')

    # Short-cut
    if yolo_folder_path == 'L':
        yolo_folder_path = r'C:\Users\lukad\Desktop\Computer Vision 7th semester project COM_ENG\dsb_dataset_raw\dsb_data'

    image_paths, label_paths, classes = load_data(yolo_folder_path)

    author = input('Insert author name: ["M", "L", "T"]\n')
    
    first = int(len(image_paths) * 1 // 3)
    second = int(len(image_paths) * 2 // 3)
    
    if author == 'M':
        image_paths = image_paths[:first]
        label_paths = label_paths[:first]
    elif author == 'L':
        image_paths = image_paths[first:second]
        label_paths = label_paths[first:second]
    elif author == 'T':
        image_paths = image_paths[second:]
        label_paths = label_paths[second:]
    else:
        print('Invalid author name')
        exit()
    
    colors = ['#d22b2b', '#389e0d', '#ffc069', '#ad8b00', '#1759ab', '#0cfabc']
    colors = [conver_hex_to_decimal_color(color) for color in colors]

    if len(image_paths) == 0 or len(label_paths) == 0 or len(image_paths) != len(label_paths):
        print('Error: Invalid folder path')
        exit()

    cv.namedWindow('Image', cv.WINDOW_GUI_NORMAL)

    index = 0
    while True:
        image_path = image_paths[index]
        label_path = label_paths[index]
        
        image_window = ImageWindow(image_path, label_path, classes, colors)
        
        action = image_window.show_image()
        
        if action == 0:
            break
        
        if index + action < 0:
            index = len(image_paths) - 1
        elif index + action >= len(image_paths):
            index = 0
        else:
            index += action
        
    cv.destroyAllWindows()
