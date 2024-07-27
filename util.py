import math

def get_center_of_box(box_points):
    x1, y1, x2, y2 = box_points
    return (x1 + x2) // 2, (y1 + y2) // 2

def is_within_distance(point1, point2, threshold=20):
    x1, y1 = point1
    x2, y2 = point2
    return math.hypot(x2 - x1, y2 - y1) <= threshold

def checkIfLeftFrame(frame_width, frame_height, coords):
    x, y = coords
    if x < 70:
        return "left"
    if y < 70:
        return "down"
    if x > frame_width - 70:
        return "right"
    if y > frame_height - 70:
        return "up"
    return 