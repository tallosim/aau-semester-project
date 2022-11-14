import glob
import os
import shutil

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
    print('Classes:',classes)
    print('Number of images:',len(label_paths))
    return image_paths, label_paths, classes

if __name__ == '__main__':
    yolo_folder_path = input('Insert folder path to YOLO:\n')

    image_paths, label_paths, classes = load_data(yolo_folder_path)

    for label_path in label_paths:
        labels = open(label_path, 'r').read().splitlines()
        for label in labels:
            if label.split(' ')[0] == '5':
                labels.remove(label)
        
        if len(labels) == 0:
            continue
        
        with open(label_path, 'w') as f:
            f.write('\n'.join(labels) + '\n')
            
        print('Removed class from', label_path)