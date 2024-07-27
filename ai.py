import cv2
import yt_dlp
from imageai.Detection import VideoObjectDetection
import math

youtube_url = "https://www.youtube.com/watch?v=jQ-axqEsdvc"

# Options for yt-dlp
ydl_opts = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
}

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

# Extract video URL using yt-dlp
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(youtube_url, download=False)
    video_url = info_dict['url']

# Open video stream with OpenCV
stream = cv2.VideoCapture(video_url)

# Initialize VideoObjectDetection with YOLOv3 model
vid_obj_detect = VideoObjectDetection()
vid_obj_detect.setModelTypeAsTinyYOLOv3()
vid_obj_detect.setModelPath("tiny-yolov3.pt")  # Change to your YOLO model path

# Load the YOLO model
vid_obj_detect.loadModel()

# Function to detect objects in each frame
currObjects = []
object_paths = {}  # Dictionary to store paths of tracked objects

def for_frame(frame_number, output_array, output_count, returned_frame):
    global currObjects, object_paths

    new_objects = []

    for itemDict in output_array:
        objectName = itemDict['name']
        boxPoints = itemDict['box_points']

        cx, cy = get_center_of_box(boxPoints)
        coords = (cx, cy)

        matched = False

        for obj in currObjects:
            obj_name, obj_coords, obj_frame = obj
            if frame_number - obj_frame > 5:
                continue  # Skip old objects

            if objectName == obj_name and is_within_distance(coords, obj_coords, threshold=20):
                new_objects.append((objectName, coords, frame_number))
                matched = True

                # Update the path for the matched object
                if objectName in object_paths:
                    object_paths[objectName].append(coords)
                else:
                    object_paths[objectName] = [coords]
                break

        if not matched:
            new_objects.append((objectName, coords, frame_number))
            # Start a new path for a new object
            object_paths[objectName] = [coords]

        # Draw the bounding box and label
        x1, y1, x2, y2 = boxPoints
        cv2.rectangle(returned_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(returned_frame, objectName, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Draw the paths
    for path in object_paths.values():
        for i in range(1, len(path)):
            cv2.line(returned_frame, path[i - 1], path[i], (0, 0, 255), 2)

    currObjects = new_objects

    cv2.imshow("YOLOv3", returned_frame)
    
    # Break if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        stream.release()
        cv2.destroyAllWindows()
        return False
    return True

# Detect objects from the video
vid_obj_detect.detectObjectsFromVideo(
    input_file_path=video_url,
    output_file_path="output_video",
    frames_per_second=60,
    log_progress=True,
    minimum_percentage_probability=30,
    per_frame_function=for_frame,
    return_detected_frame=True
)
