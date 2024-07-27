import cv2
from imageai.Detection import VideoObjectDetection
import math

video_file_path = r"C:\Users\dan14027\OneDrive - Esri\Desktop\MicrosoftTeams-video (1).mp4"

def get_center_of_box(box_points):
    x1, y1, x2, y2 = box_points
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    return cx, cy

def is_within_distance(point1, point2, threshold=20):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance <= threshold

#opens the given video with open CV
stream = cv2.VideoCapture(video_file_path)

#Initializes VideoObjectDetection object with model type as Tiny YOLOV3
vid_obj_detect = VideoObjectDetection()
vid_obj_detect.setModelTypeAsTinyYOLOv3()
vid_obj_detect.setModelPath("tiny-yolov3.pt") 
vid_obj_detect.loadModel()

# Function to detect objects in each frame
currObjects = []
object_paths = {}  # dict to store paths of tracked objects
object_disappear_frame_count = {}  # tracks when an object dissapear

next_object_id = 0  # unique ID counter

def for_frame(frame_number, output_array, output_count, returned_frame):
    global currObjects, object_paths, object_disappear_frame_count, next_object_id

    new_objects = []

    for itemDict in output_array:
        objectName = itemDict['name']
        boxPoints = itemDict['box_points']

        cx, cy = get_center_of_box(boxPoints)
        coords = (cx, cy)

        matched = False
        object_id = None

        for obj in currObjects:
            obj_id, obj_name, obj_coords, obj_frame = obj
            if frame_number - obj_frame > 60:
                continue  # Skip old objects

            if objectName == obj_name and is_within_distance(coords, obj_coords, threshold=60):
                new_objects.append((obj_id, objectName, coords, frame_number))
                matched = True
                object_id = obj_id

                # Update the path for the matched object
                if obj_id in object_paths:
                    object_paths[obj_id].append(coords)
                else:
                    object_paths[obj_id] = [coords]

                # Reset disappear frame count
                object_disappear_frame_count[obj_id] = frame_number
                break

        if not matched:
            # Assign a new ID to the new object
            object_id = next_object_id
            next_object_id += 1
            new_objects.append((object_id, objectName, coords, frame_number))
            # Start a new path for a new object
            object_paths[object_id] = [coords]
            # Initialize disappear frame count
            object_disappear_frame_count[object_id] = frame_number

        # Draw the bounding box and label
        x1, y1, x2, y2 = boxPoints
        cv2.rectangle(returned_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(returned_frame, f"{objectName} {object_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Remove objects that have disappeared for more than 10 frames
    currObjects = [obj for obj in new_objects if frame_number - object_disappear_frame_count[obj[0]] <= 10]

    # Remove paths for objects that have disappeared for more than 10 frames
    object_paths = {obj_id: path for obj_id, path in object_paths.items() if frame_number - object_disappear_frame_count[obj_id] <= 10}

    # Draw the paths
    for path in object_paths.values():
        for i in range(1, len(path)):
            cv2.line(returned_frame, path[i - 1], path[i], (0, 0, 255), 2)

    cv2.imshow("YOLOv3", returned_frame)
    
    # Break if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        stream.release()
        cv2.destroyAllWindows()
        return False
    return True

# Detect objects from the video
vid_obj_detect.detectObjectsFromVideo(
    input_file_path=video_file_path,
    output_file_path="output_video",
    frames_per_second=60,
    log_progress=True,
    minimum_percentage_probability=30,
    per_frame_function=for_frame,
    return_detected_frame=True
)
