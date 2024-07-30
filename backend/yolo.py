import cv2
from imageai.Detection import VideoObjectDetection


class YOLO:
    def __init__(self, model_path):
        self.model_path = model_path
        self.detector = VideoObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath(self.model_path)
        self.detector.loadModel()

    def detect_objects(self, frame):
        detected_frame, detections = self.detector.detectObjectsFromImage(
            input_image=frame, input_type="array", output_type="array"
        )
        return detected_frame, detections
