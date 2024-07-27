import cv2
from imageai.Detection import VideoObjectDetection
import asyncio
import websockets
import json
from util import get_center_of_box, is_within_distance, checkIfLeftFrame


class VideoObjectTracker:
    def __init__(self, video_file_path, model_path, websocket_url):
        self.video_file_path = video_file_path
        self.websocket_url = websocket_url
        self.stream = cv2.VideoCapture(video_file_path)
        self.currObjects = []
        self.object_paths = {}  # dict to store paths of tracked objects
        self.object_disappear_frame_count = {}  # tracks when an object disappears
        self.next_object_id = 0  # unique ID counter

        # Initialize VideoObjectDetection object with Tiny YOLOV3 model
        self.vid_obj_detect = VideoObjectDetection()
        self.vid_obj_detect.setModelTypeAsTinyYOLOv3()
        self.vid_obj_detect.setModelPath(model_path)
        self.vid_obj_detect.loadModel()

    async def send_message_to_websocket(self, message):
        print("Sending message to WebSocket")
        async with websockets.connect(self.websocket_url) as websocket:
            await websocket.send(json.dumps(message))

    def for_frame(self, frame_number, output_array, output_count, returned_frame):
        frame_height, frame_width, _ = returned_frame.shape
        new_objects = []

        for itemDict in output_array:
            objectName = itemDict["name"]
            boxPoints = itemDict["box_points"]

            coords = get_center_of_box(boxPoints)
            matched = False

            for obj_id, obj_name, obj_coords, obj_frame in self.currObjects:
                if frame_number - obj_frame > 60:
                    continue  # Skip old objects

                if objectName == obj_name and is_within_distance(
                    coords, obj_coords, threshold=60
                ):
                    new_objects.append((obj_id, objectName, coords, frame_number))
                    matched = True

                    # Update the path for the matched object
                    self.object_paths.setdefault(obj_id, []).append(coords)
                    # Reset disappear frame count
                    self.object_disappear_frame_count[obj_id] = frame_number
                    break

            if not matched:
                # Assign a new ID to the new object
                obj_id = self.next_object_id
                self.next_object_id += 1
                new_objects.append((obj_id, objectName, coords, frame_number))
                # Start a new path for a new object
                self.object_paths[obj_id] = [coords]
                # Initialize disappear frame count
                self.object_disappear_frame_count[obj_id] = frame_number

            # Draw the bounding box and label
            x1, y1, x2, y2 = boxPoints
            cv2.rectangle(returned_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                returned_frame,
                f"{objectName} {obj_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

        # Remove objects that have disappeared for more than 10 frames
        self.currObjects = [
            obj
            for obj in new_objects
            if frame_number - self.object_disappear_frame_count[obj[0]] <= 10
        ]
        newObjectPaths = {}
        for obj_id, path in self.object_paths.items():
            if frame_number - self.object_disappear_frame_count[obj_id] <= 10:
                newObjectPaths[obj_id] = path
            else:
                dir = checkIfLeftFrame(frame_width, frame_height, path[-1])
                if not dir:
                    print("did not leave")
                else:
                    print("!!!", dir)
                    # Call WebSocket function to send message
                    message = {
                        "object_id": obj_id,
                        "direction": dir,
                        "path": path,
                        "frame_height": frame_height,
                        "frame_width": frame_width,
                    }
                    asyncio.run(self.send_message_to_websocket(message))
                    print(path)
                    print(f"Frame height: {frame_height}, Frame width: {frame_width}")

        self.object_paths = newObjectPaths

        # Draw the paths
        for path in self.object_paths.values():
            for i in range(1, len(path)):
                cv2.line(returned_frame, path[i - 1], path[i], (0, 0, 255), 2)

        cv2.imshow("YOLOv3", returned_frame)

        # Break if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.stream.release()
            cv2.destroyAllWindows()
            return False
        return True

    def start_tracking(self):
        self.vid_obj_detect.detectObjectsFromVideo(
            input_file_path=self.video_file_path,
            output_file_path="output_video",
            frames_per_second=60,
            log_progress=True,
            minimum_percentage_probability=30,
            per_frame_function=self.for_frame,
            return_detected_frame=True,
        )
