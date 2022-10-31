import cv2
import numpy as np
import json
import os
import shutil
import glob
from sklearn.model_selection import train_test_split
import yaml


METADATA_PATH = 'data/project-1-at-2022-10-20-09-37-9a7c9b50.json'
ANNOTAION_TO_FILENAME = {
    3: 'video_3.mp4',
    4: 'video_4.mp4',
    5: 'video_2.mp4',
    6: 'video_1.mp4',
    9: 'Video7_1.mp4',
    10: 'Video7_2.mp4',
    11: 'video_5_1.mp4',
    12: 'Video7_3.mp4',
    13: 'Video7_4.mp4',
    14: 'video_5_2.mp4',
    15: 'Video7_5.mp4',
    16: 'Video7_6.mp4',
    17: 'Video7_7.mp4',
    18: 'Video7_8.mp4',
    19: 'Video7_9.mp4',
    23: 'video_8.MP4',
    24: 'Video7_13.mp4',
}
VIDEO_FOLDER_PATH = 'videos/'
IMAGES_FOLDER_PATH = 'images/'
MOVE_SAMPLE_RATIO = 0.2
STOP_SAMPLE_COUNT = 5
STOPPED_SECTIONS = {
    4: [(0, 400)],
    6: [(0, 8000)],
    23: [(0, 7640)],
}
YOLO_DATASET_PATH = 'yolo/'
LABELS = ['1_AND_2', '1_AND_4', '1_AND_3', '2_AND_4', 'OTHER']
MIN_SIZE_X = 30
MIN_SIZE_Y = 40
PADDING = 0.05
TEST_SPLIT = 0.2
VAL_SPLIT = 0.2


def get_label_id(label):
    if '1_AND_2' in label:
        return 0
    if '1_AND_4' in label:
        return 1
    if '1_AND_3' in label:
        return 2
    if '2_AND_4' in label:
        return 3
    
    return 4



print('\nLoading metadata...')

with open(METADATA_PATH) as f:
    data = json.load(f)



print('\nExtracting keyframe sequences...')

video_keyframe_sequences = dict()
frame_counts = dict()

for annotation in data:
    if annotation['id'] in ANNOTAION_TO_FILENAME:
        print(f"Processing {ANNOTAION_TO_FILENAME[annotation['id']]} ({annotation['id']})")
        
        labels = annotation['annotations'][0]['result']
        keyframe_sequences = list()
        
        for label_index, label in enumerate(labels):
            label_type = label['value']['labels'][0]
            frame_counts[annotation['id']] = label['value']['framesCount']
            
            sub_sequence = list()
            is_enabled = False
            
            for frame in label['value']['sequence']:
                frame['label_type'] = label_type
                frame['label_index'] = label_index
                
                if frame['frame'] > 0:
                    frame['frame'] = frame['frame'] - 1
                
                if frame['enabled'] == True:
                    is_enabled = True
                    sub_sequence.append(frame)
                elif frame['enabled'] == False and is_enabled:
                    sub_sequence.append(frame)
                    keyframe_sequences.append(sub_sequence)
                    sub_sequence = list()
            
            if len(sub_sequence) > 0:  
                keyframe_sequences.append(sub_sequence)
        
        video_keyframe_sequences[annotation['id']] = keyframe_sequences
        


print('\nInterpolating frames...')
        
video_frames = dict()
for annotation_id, keyframe_sequences in video_keyframe_sequences.items():
    print(f'Processing {ANNOTAION_TO_FILENAME[annotation_id]} ({annotation_id})')
    frames = dict()

    for i in range(frame_counts[annotation_id]):
        labels = list()
        
        for keyframe_sequence in keyframe_sequences:
            first_frame = keyframe_sequence[0]
            last_frame = keyframe_sequence[-1]
            
            if first_frame['frame'] <= i and i <= last_frame['frame']:
                keyframe = list(filter(lambda frame: frame['frame'] == i, keyframe_sequence))
                if len(keyframe) > 0:
                    frame = {
                        'label_type': keyframe[0]['label_type'],
                        'x': keyframe[0]['x'],
                        'y': keyframe[0]['y'],
                        'width': keyframe[0]['width'],
                        'height': keyframe[0]['height'],
                        'keyframe': True
                    }
                    
                    labels.append(frame)
                    continue
                
                keyframe_before = list(filter(lambda frame: frame['frame'] < i, keyframe_sequence))[-1]
                keyframe_after = list(filter(lambda frame: frame['frame'] > i, keyframe_sequence))[0]
                
                multiplier = (i - keyframe_before['frame']) / (keyframe_after['frame'] - keyframe_before['frame'])
                
                frame = {
                    'label_type': keyframe_before['label_type'],
                    'x': keyframe_before['x'] + (keyframe_after['x'] - keyframe_before['x']) * multiplier,
                    'y': keyframe_before['y'] + (keyframe_after['y'] - keyframe_before['y']) * multiplier,
                    'width': keyframe_before['width'] + (keyframe_after['width'] - keyframe_before['width']) * multiplier,
                    'height': keyframe_before['height'] + (keyframe_after['height'] - keyframe_before['height']) * multiplier,
                    'keyframe': False
                }
                
                labels.append(frame)
        
        if len(labels) > 0:
            frames[i] = labels
            
    video_frames[annotation_id] = frames



print('\nRandom sampling...')

video_frame_list = dict()

for annotation_id, frames in video_frames.items():
    print(
        f'Processing {ANNOTAION_TO_FILENAME[annotation_id]} ({annotation_id})')

    frame_list = np.array(list(frames.keys()))

    if annotation_id in STOPPED_SECTIONS:
        stop_list = list()
        for sections in STOPPED_SECTIONS[annotation_id]:
            stop_list += list(range(sections[0], sections[1], 1))
        stop_list = np.array(stop_list)
        move_list = frame_list[~np.isin(frame_list, stop_list)]
        
        stop_selected_frame_list = np.random.choice(stop_list, STOP_SAMPLE_COUNT, replace=False)
        move_selected_frame_list = np.random.choice(move_list, int(len(move_list) * MOVE_SAMPLE_RATIO), replace=False)
        
        selected_frame_list = np.concatenate((stop_selected_frame_list, move_selected_frame_list))
    else:
        selected_frame_list = np.random.choice(frame_list, int(len(frame_list) * MOVE_SAMPLE_RATIO))

    selected_frame_list = list(sorted(selected_frame_list))
    print(f'Found {len(selected_frame_list)} frames')

    video_frame_list[annotation_id] = selected_frame_list
 
 

print('\nGenerating training data...')

# A dangerous function, but it's ok for this case
shutil.rmtree(YOLO_DATASET_PATH, ignore_errors=True)

# Create folder system
os.makedirs(os.path.join(YOLO_DATASET_PATH, 'images', 'train'), exist_ok=True)
os.makedirs(os.path.join(YOLO_DATASET_PATH, 'labels', 'train'), exist_ok=True)

# Generate images and labels
for annotation_id, frame_list in video_frame_list.items():
    print(f'Processing {ANNOTAION_TO_FILENAME[annotation_id]} ({annotation_id})')
    file_path = os.path.join(VIDEO_FOLDER_PATH, ANNOTAION_TO_FILENAME[annotation_id])
    
    frames = video_frames[annotation_id]
    
    cap = cv2.VideoCapture(file_path)
    
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    min_size_x = MIN_SIZE_X / original_width
    min_size_y = MIN_SIZE_Y / original_height
    
    frame_id = -1
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        
        if ret == False:
            break
        
        if frame_id in frame_list:
            labels = frames[frame_id]
            
            yolo_labels = list()
            for i, label in enumerate(labels):
                label_type = label['label_type']
                label_id = get_label_id(label_type)
                
                # Normalize coordinates
                x = label['x'] / 100.0
                y = label['y'] / 100.0
                w = label['width'] / 100.0
                h = label['height'] / 100.0
                
                # Add padding
                x = x - (w * PADDING)
                y = y - (h * PADDING)
                w = w + (w * PADDING * 2)
                h = h + (h * PADDING * 2)
                
                # Move coordinates to center
                x = x + (w / 2)
                y = y + (h / 2)
                
                # Make sure that the coordinates are in the range [0, 1]
                x = max(0., min(1., x))
                y = max(0., min(1., y))
                
                if min_size_x <= w and min_size_y <= h:
                    yolo_labels.append(' '.join([str(label_id), ' '.join(['{:.6f}'.format(v) for v in [x, y, w, h]])]))
            
            if len(yolo_labels) > 0:
                # Save image
                cv2.imwrite(os.path.join(YOLO_DATASET_PATH, 'images', 'train', f'{annotation_id}_{frame_id}.jpg'), frame)
                
                # Save labels
                with open(os.path.join(YOLO_DATASET_PATH, 'labels', 'train', f'{annotation_id}_{frame_id}.txt'), 'w') as f:
                    for label in yolo_labels:
                        f.write(f'{label}\n')
        
        frame_id += 1
    
    cap.release()



print('\nCreating train / test / val split...')

images = glob.glob(os.path.join(YOLO_DATASET_PATH, 'images', 'train', '*.jpg'))
labels = glob.glob(os.path.join(YOLO_DATASET_PATH, 'labels', 'train', '*.txt'))

images = list(sorted(images))
labels = list(sorted(labels))

train_images, test_images, train_labels, test_labels = train_test_split(images, labels, test_size=TEST_SPLIT)
train_images, val_images, train_labels, val_labels = train_test_split(train_images, train_labels, test_size=VAL_SPLIT)

print(f'Train: {len(train_images)}')
print(f'Val: {len(val_images)}')
print(f'Test: {len(test_images)}')        

os.makedirs(os.path.join(YOLO_DATASET_PATH, 'images', 'test'), exist_ok=True)
os.makedirs(os.path.join(YOLO_DATASET_PATH, 'labels', 'test'), exist_ok=True)

os.makedirs(os.path.join(YOLO_DATASET_PATH, 'images', 'valid'), exist_ok=True)
os.makedirs(os.path.join(YOLO_DATASET_PATH, 'labels', 'valid'), exist_ok=True)

for image, label in zip(test_images, test_labels):
    shutil.move(image, os.path.join(YOLO_DATASET_PATH, 'images', 'test'))
    shutil.move(label, os.path.join(YOLO_DATASET_PATH, 'labels', 'test'))
    
for image, label in zip(val_images, val_labels):
    shutil.move(image, os.path.join(YOLO_DATASET_PATH, 'images', 'valid'))
    shutil.move(label, os.path.join(YOLO_DATASET_PATH, 'labels', 'valid'))
    


print('\nCreating class.txt...')

with open(os.path.join(YOLO_DATASET_PATH, 'classes.txt'), 'w') as f:
    for label in LABELS:
        f.write(f'{label}\n')
        


print('\nCreating data.yaml...')
        
yaml_config = {
    'train': os.path.join(YOLO_DATASET_PATH, 'images', 'train'),
    'val': os.path.join(YOLO_DATASET_PATH, 'images', 'valid'),
    'test': os.path.join(YOLO_DATASET_PATH, 'images', 'test'),
    'nc': len(LABELS),
    'names': LABELS
}

with open(os.path.join(YOLO_DATASET_PATH, 'data.yaml'), 'w') as f:
    yaml.dump(yaml_config, f)



print('\nDone!')
