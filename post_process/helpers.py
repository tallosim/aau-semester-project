
def calc_iou(box1, box2):
    _, x1, y1, w1, h1, _ = box1
    _, x2, y2, w2, h2, _ = box2
    
    x1_min, x1_max = x1 - w1/2, x1 + w1/2
    y1_min, y1_max = y1 - h1/2, y1 + h1/2

    x2_min, x2_max = x2 - w2/2, x2 + w2/2
    y2_min, y2_max = y2 - h2/2, y2 + h2/2
    
    inter_x1 = max(x1_min, x2_min)
    inter_y1 = max(y1_min, y2_min)
    
    inter_x2 = min(x1_max, x2_max)
    inter_y2 = min(y1_max, y2_max)
    
    inter_w = inter_x2 - inter_x1
    inter_h = inter_y2 - inter_y1
    inter_area = inter_w * inter_h
    
    union_area = w1 * h1 + w2 * h2 - inter_area
    
    return inter_area / union_area

def is_overlaping(box1, box2):
    _, x1, y1, w1, h1, _ = box1
    _, x2, y2, w2, h2, _ = box2

    x1_min, x1_max = x1 - w1/2, x1 + w1/2
    y1_min, y1_max = y1 - h1/2, y1 + h1/2

    x2_min, x2_max = x2 - w2/2, x2 + w2/2
    y2_min, y2_max = y2 - h2/2, y2 + h2/2

    if x1_max < x2_min or x1_min > x2_max:
        return False

    if y1_max < y2_min or y1_min > y2_max:
        return False

    return True

def conver_hex_to_decimal_color(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))