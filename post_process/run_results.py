import cv2 as cv
import glob
import os
import time
from helpers import *

EXPERIMENT_NAME = 'exp'
VIDEO_PATH = 'video_2.mp4'
LABEL_PATH = 'labels'
CLASSES_PATH = 'classes.txt'
RADIUS = 3
COLORS = ['#d22b2b', '#389e0d', '#ffc069', '#ad8b00', '#1759ab', '#0cfabc']

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

classes = open(os.path.join(BASE_PATH, EXPERIMENT_NAME, CLASSES_PATH), 'r').read().splitlines()

label_paths = glob.glob(os.path.join(BASE_PATH, EXPERIMENT_NAME, LABEL_PATH, '*.txt'))
label_paths = list(sorted(label_paths, key=lambda x: int(x.split('/')[-1].split('.')[0].split('_')[-1])))
labels = {}

for label_path in label_paths:
    frame_number = int(label_path.split(os.sep)[-1].split('.')[0].split('_')[-1])
    
    lines = open(label_path, 'r').read().splitlines()

    boxes = []

    for line in lines:
        type, x, y, w, h, conf = line.split(' ')
        x, y, w, h, conf = float(x), float(y), float(w), float(h), float(conf)
        class_type = int(type)
        
        boxes.append([class_type, x, y, w, h, conf])
    
    for i, bi in enumerate(boxes):
        for j, bj in enumerate(boxes[i+1:]):
            iou = calc_iou(bi, bj)
            
            if iou > 0.8:
                if bi[5] > bj[5]:
                    boxes.remove(boxes[j])
                else:
                    boxes.remove(boxes[i])
    
    labels[frame_number] = boxes
print(f'Loaded {len(labels)} frames')

signal_sequences = []

for i, (frame_number, boxes) in enumerate(labels.items()):
    for box in boxes:
        added = False
        
        for signal_sequence in signal_sequences:
            last_frame, last_box = signal_sequence[-1]
            if calc_iou(box, last_box) > 0.5 and frame_number - last_frame < 10:
                signal_sequence.append([frame_number, box])
                added = True
                break
            
        if not added:
            signal_sequences.append([[frame_number, box]])

print()
print([len(x) for x in signal_sequences])

for i, signal_sequence in enumerate(signal_sequences):
    if len(signal_sequence) < 50:
        print(f'Removing signal sequence {i} with length {len(signal_sequence)}')
        signal_sequences.remove(signal_sequence)
        
print([len(x) for x in signal_sequences])
print()

           
def find_boxes_in_frame(frame_number):
    boxes = []
    for signal_sequence in signal_sequences:
        for i, (frame, box) in enumerate(signal_sequence):
            if frame == frame_number:
                boxes.append(box)
                break
    return boxes            
   
            
colors = [conver_hex_to_decimal_color(color) for color in COLORS]

cap = cv.VideoCapture(os.path.join(BASE_PATH, EXPERIMENT_NAME, VIDEO_PATH))
frame_index = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    cv.putText(frame, str(frame_index), (10, 30), 0, 1, (0, 0, 255), 2)
    
    boxes = find_boxes_in_frame(frame_index)
    
    if len(boxes) > 0:
        for box in boxes:
            class_type, x, y, w, h, conf = box
            
            pixel_x = int(x * frame.shape[1])
            pixel_y = int(y * frame.shape[0])
            pixel_w = int(w * frame.shape[1])
            pixel_h = int(h * frame.shape[0])

            pixel_x = pixel_x - int(pixel_w / 2)
            pixel_y = pixel_y - int(pixel_h / 2)
            
            color = colors[class_type]
            class_name = classes[class_type]
            box_label = f'{class_name} {conf:.2f}'
            
            p1 = (pixel_x, pixel_y)
            p2 = (pixel_x + pixel_w, pixel_y)
            p3 = (pixel_x + pixel_w, pixel_y + pixel_h)
            p4 = (pixel_x, pixel_y + pixel_h)
            
            cv.rectangle(frame, (p1[0]-RADIUS, p1[1]-RADIUS), (p1[0]+RADIUS, p1[1]+RADIUS), color, -1)
            cv.rectangle(frame, (p2[0]-RADIUS, p2[1]-RADIUS), (p2[0]+RADIUS, p2[1]+RADIUS), color, -1)
            cv.rectangle(frame, (p3[0]-RADIUS, p3[1]-RADIUS), (p3[0]+RADIUS, p3[1]+RADIUS), color, -1)
            cv.rectangle(frame, (p4[0]-RADIUS, p4[1]-RADIUS), (p4[0]+RADIUS, p4[1]+RADIUS), color, -1)

            cv.rectangle(frame, p1, p3, color, 2)
            cv.putText(frame, box_label, (p1[0], p1[1] - 12), 0, 0.8, color, 2)
    
    cv.imshow('frame', frame)
    cv.waitKey(1)
    time.sleep(0.005)
    
    frame_index += 1

cap.release()