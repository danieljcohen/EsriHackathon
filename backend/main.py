import json
import logging
import asyncio
from fastapi import FastAPI, WebSocket, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from fastapi.responses import StreamingResponse
import time
import cv2
import asyncio
from imageai.Detection import VideoObjectDetection
from util import get_center_of_box, is_within_distance, checkIfLeftFrame


class VideoObjectTracker:
    def __init__(self, video_file_path, model_path, client):
        self.video_file_path = video_file_path
        self.stream = cv2.VideoCapture(video_file_path)
        self.currObjects = []
        self.object_paths = {}  # dict to store paths of tracked objects
        self.object_disappear_frame_count = {}  # tracks when an object disappears
        self.next_object_id = 0  # unique ID counter
        self.client = client  # WebSocket client

        # Initialize VideoObjectDetection object with Tiny YOLOV3 model
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

            # Only process if the object is a person
            if objectName.lower() != "person":
                continue

            coords = get_center_of_box(boxPoints)
            matched = False

            for obj_id, obj_name, obj_coords, obj_frame in self.currObjects:
                if frame_number - obj_frame > 50:
                    continue  # Skip old objects

                if objectName == obj_name and is_within_distance(
                    coords, obj_coords, threshold=40
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

            # Check if the center of two bounding boxes are within 20 pixels
            close_objects = [
                obj
                for obj in new_objects
                if is_within_distance(coords, obj[2], threshold=20)
            ]

            if len(close_objects) == 1:
                # Draw the bounding box and label
                x1, y1, x2, y2 = boxPoints
                cv2.rectangle(returned_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    returned_frame,
                    f"{objectName}",
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
            if frame_number - self.object_disappear_frame_count[obj[0]] <= 30
        ]
        newObjectPaths = {}
        for obj_id, path in self.object_paths.items():
            if frame_number - self.object_disappear_frame_count[obj_id] <= 30:
                newObjectPaths[obj_id] = path
            else:
                dir = checkIfLeftFrame(frame_width, frame_height, path[-1])
                if not dir:
                    print("did not leave")
                else:
                    print(dir)
                    # Call WebSocket function to send message
                    message = {
                        "object_name": obj_name,
                        "direction": dir,
                        "path": path,
                        "frame_height": frame_height,
                        "frame_width": frame_width,
                    }
                    print("WEBSOCKET", message)
                    send_loc_data(message)

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
            frames_per_second=30,
            log_progress=True,
            minimum_percentage_probability=30,
            per_frame_function=self.for_frame,
            return_detected_frame=True,
        )


app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None


@app.get("/healthz")
async def health_check():
    return {"Server": "Live"}


video_file_path = "../media/two_ppl_rendered.mp4"
video_capture = cv2.VideoCapture(video_file_path)
fps = video_capture.get(cv2.CAP_PROP_FPS)
frame_delay = 1 / fps


def generate_frames():
    global video_capture
    while True:
        success, frame = video_capture.read()
        if not success:
            video_capture = cv2.VideoCapture(video_file_path)  # Restart the video
            success, frame = video_capture.read()
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(frame_delay)


@app.get("/video_stream")
async def video_stream():
    return StreamingResponse(
        generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/video")
async def video_feed():
    success, frame = video_capture.read()
    if not success:
        return Response(status_code=404)
    _, buffer = cv2.imencode(".jpg", frame)
    frame = buffer.tobytes()
    return Response(content=frame, media_type="image/jpeg")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global client
    await websocket.accept()
    client = websocket
    print("client connected: ", client)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        client = None
        print("client disconnected: ", client)


def send_loc_data(data):
    global client
    print("client: ", client)
    if client:
        print("sending web socket...", json.dumps(data))
        asyncio.run(client.send_text(json.dumps(data)))
        time.sleep(2)
        data["direction"] = "right"
        asyncio.run(client.send_text(json.dumps(data)))


if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    video_file_path = "../media/two_ppl.mp4"
    model_path = "tiny-yolov3.pt"

    tracker = VideoObjectTracker(video_file_path, model_path, client)

    # Run FastAPI server in a separate thread
    try:
        server_thread = Thread(
            target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000)
        )
        server_thread.start()

        # # Start tracking
        tracker.start_tracking()
    except Exception as e:
        print(f"Error running Flask app: {e}")
    finally:
        video_capture.release()
