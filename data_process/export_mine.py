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
    return image_paths, label_paths, classes

if __name__ == '__main__':
    yolo_folder_path = input('Insert folder path to YOLO:\n')

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
        
    new_folder_path = input('Insert new folder path:\n')
    
    for path in ['train', 'test', 'valid']:
        os.makedirs(os.path.join(new_folder_path, 'labels', path), exist_ok=True)
    
    for image_path, label_path in zip(image_paths, label_paths):
        shutil.copyfile(label_path, os.path.join(new_folder_path, 'labels', label_path.split('/')[-2], label_path.split('/')[-1]))