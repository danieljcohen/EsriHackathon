import cv2
import json
from imageai.Detection import VideoObjectDetection

def get_center_of_box(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def is_within_distance(coord1, coord2, threshold=40):
    return ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5 < threshold

def checkIfLeftFrame(frame_width, frame_height, coord, margin=70):
    x, y = coord
    if x <= margin:
        return "left"
    elif x >= frame_width - margin:
        return "right"
    elif y <= margin:
        return "top"
    elif y >= frame_height - margin:
        return "bottom"
    return None


class VideoObjectTracker:
    def __init__(self, model_path):
        self.stream = cv2.VideoCapture(0)
        self.currObjects = []
        self.object_paths = {}
        self.object_disappear_frame_count = {}
        self.next_object_id = 0
        self.exit_message = ""

        self.vid_obj_detect = VideoObjectDetection()
        self.vid_obj_detect.setModelTypeAsTinyYOLOv3()
        self.vid_obj_detect.setModelPath(model_path)
        self.vid_obj_detect.loadModel()

    def for_frame(self, frame_number, output_array, output_count, returned_frame):
        frame_height, frame_width, _ = returned_frame.shape
        new_objects = []

        for itemDict in output_array:
            objectName = itemDict["name"]
            boxPoints = itemDict["box_points"]

            if objectName.lower() != "person":
                continue

            coords = get_center_of_box(boxPoints)
            matched = False

            for obj_id, obj_name, obj_coords, obj_frame in self.currObjects:
                if frame_number - obj_frame > 50:
                    continue

                if objectName == obj_name and is_within_distance(coords, obj_coords, threshold=150):
                    new_objects.append((obj_id, objectName, coords, frame_number))
                    matched = True
                    self.object_paths.setdefault(obj_id, []).append(coords)
                    self.object_disappear_frame_count[obj_id] = frame_number
                    break

            if not matched:
                obj_id = self.next_object_id
                self.next_object_id += 1
                new_objects.append((obj_id, objectName, coords, frame_number))
                self.object_paths[obj_id] = [coords]
                self.object_disappear_frame_count[obj_id] = frame_number

            close_objects = [obj for obj in new_objects if is_within_distance(coords, obj[2], threshold=20)]

            if len(close_objects) == 1:
                x1, y1, x2, y2 = boxPoints
                cv2.rectangle(returned_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(returned_frame, f"{objectName}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        self.currObjects = [obj for obj in new_objects if frame_number - self.object_disappear_frame_count[obj[0]] <= 20]
        newObjectPaths = {}
        for obj_id, path in self.object_paths.items():
            if frame_number - self.object_disappear_frame_count[obj_id] <= 20:
                newObjectPaths[obj_id] = path
            else:
                direction = checkIfLeftFrame(frame_width, frame_height, path[-1])
                if direction:
                    self.exit_message = f"User exited to the {direction}"
                    message = {
                        "object_id": obj_id,
                        "direction": direction,
                        "path": path,
                        "frame_height": frame_height,
                        "frame_width": frame_width,
                    }
                    print(json.dumps(message))

        self.object_paths = newObjectPaths

        for path in self.object_paths.values():
            for i in range(1, len(path)):
                cv2.line(returned_frame, path[i - 1], path[i], (0, 0, 255), 2)

        if self.exit_message:
            cv2.putText(returned_frame, self.exit_message, (10, frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("YOLOv3", returned_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.stream.release()
            cv2.destroyAllWindows()
            return False
        return True

    def start_tracking(self):
        self.vid_obj_detect.detectObjectsFromVideo(
            camera_input=self.stream,
            output_file_path="output_video",
            frames_per_second=30,
            log_progress=True,
            minimum_percentage_probability=30,
            per_frame_function=self.for_frame,
            return_detected_frame=True,
        )

if __name__ == "__main__":
    model_path = "tiny-yolov3.pt"
    tracker = VideoObjectTracker(model_path)
    tracker.start_tracking()
