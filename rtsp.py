import cv2
from imageai.Detection import VideoObjectDetection
from util import get_center_of_box, is_within_distance, checkIfLeftFrame

video_file_path = r"esrihackathon\src\components\arcgis-asset-tracker\media\MicrosoftTeams-video (1).mp4"

# Open the video with OpenCV
stream = cv2.VideoCapture(video_file_path)

# Initialize VideoObjectDetection object with Tiny YOLOV3 model
vid_obj_detect = VideoObjectDetection()
vid_obj_detect.setModelTypeAsTinyYOLOv3()
vid_obj_detect.setModelPath("tiny-yolov3.pt") 
vid_obj_detect.loadModel()

# Tracking variables
currObjects = []
object_paths = {}  # dict to store paths of tracked objects
object_disappear_frame_count = {}  # tracks when an object disappears
next_object_id = 0  # unique ID counter

def for_frame(frame_number, output_array, output_count, returned_frame):
    global currObjects, object_paths, object_disappear_frame_count, next_object_id
    frame_height, frame_width, _ = returned_frame.shape
    new_objects = []

    for itemDict in output_array:
        objectName = itemDict['name']
        boxPoints = itemDict['box_points']

        coords = get_center_of_box(boxPoints)
        matched = False

        for obj_id, obj_name, obj_coords, obj_frame in currObjects:
            if frame_number - obj_frame > 60:
                continue  # Skip old objects

            if objectName == obj_name and is_within_distance(coords, obj_coords, threshold=60):
                new_objects.append((obj_id, objectName, coords, frame_number))
                matched = True

                # Update the path for the matched object
                object_paths.setdefault(obj_id, []).append(coords)
                # Reset disappear frame count
                object_disappear_frame_count[obj_id] = frame_number
                break

        if not matched:
            # Assign a new ID to the new object
            obj_id = next_object_id
            next_object_id += 1
            new_objects.append((obj_id, objectName, coords, frame_number))
            # Start a new path for a new object
            object_paths[obj_id] = [coords]
            # Initialize disappear frame count
            object_disappear_frame_count[obj_id] = frame_number

        # Draw the bounding box and label
        x1, y1, x2, y2 = boxPoints
        cv2.rectangle(returned_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(returned_frame, f"{objectName} {obj_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Remove objects that have disappeared for more than 10 frames
    currObjects = [obj for obj in new_objects if frame_number - object_disappear_frame_count[obj[0]] <= 10]
    newObjectPaths = {}
    for obj_id, path in object_paths.items():
        if frame_number - object_disappear_frame_count[obj_id] <= 10:
            newObjectPaths[obj_id] = path
        else:
            dir = checkIfLeftFrame(frame_width, frame_height, path[-1])
            if not dir:
                print("did not leave")
            else:
                print(dir)
            print(path)
            print(f"Frame height: {frame_height}, Frame width: {frame_width}")

    object_paths = newObjectPaths

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
