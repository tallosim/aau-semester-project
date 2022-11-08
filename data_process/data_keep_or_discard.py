import cv2 as cv
import glob
import os


def load_data(folder_path):
    image_paths = glob.glob(os.path.join(folder_path, 'images', 'train', '*.jpg'))
    label_paths = glob.glob(os.path.join(folder_path, 'labels', 'train', '*.txt'))
    
    image_paths = list(sorted(image_paths))
    label_paths = list(sorted(label_paths))

    print("Received folder path:",folder_path)
    print(len(image_paths),"Image path:",image_paths)
    print(len(label_paths),"Label path:",label_paths)
    return image_paths, label_paths


def show_image(image_path, label_path):
    image = cv.imread(image_path)
    print("Received image path:",image_path)

    bounding_boxes_read = open(label_path, 'r').read().splitlines()
    image_with_bounding = image.copy()

    for x in range(len(bounding_boxes_read)):
        count, x, y, w, h = bounding_boxes_read[x].split(' ')
        count, x, y, w, h = float(count), float(x), float(y), float(w), float(h)
        print("Label data:",count, x, y, w, h)

        pixel_x = int(x * image.shape[1])
        pixel_y = int(y * image.shape[0])
        pixel_width = int(w * image.shape[1])
        pixel_height = int(h * image.shape[0])

        pixel_x = pixel_x - int(pixel_width / 2)
        pixel_y = pixel_y - int(pixel_height / 2)

        cv.rectangle(image_with_bounding, (pixel_x, pixel_y), (pixel_x+pixel_width, pixel_y+pixel_height), (255,0,0), 5)

    cv.imshow("Image",image_with_bounding)
    cv.waitKey(0)


if __name__ == '__main__':
    yolo_folder_path = input('Insert folder path to YOLO:\n')

    # Short-cut
    if yolo_folder_path == "L":
        yolo_folder_path = r'C:\Users\lukad\Desktop\Computer Vision 7th semester project COM_ENG\yolo'

    image_paths, label_paths = load_data(yolo_folder_path)
    for i in range(len(image_paths)):
        show_image(image_paths[i], label_paths[i])

    pass