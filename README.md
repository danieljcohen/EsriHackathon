# ArcGIS Care

Real-time inventory tracking tool enhancing efficiency and reducing operational challenges in hospitals.

## Overview

ArcGIS Care leverages real-time detection and tracking of critical medical equipment, providing hospitals with the tools to monitor and manage resources efficiently. This project integrates machine learning, GIS, and WebSocket technology to ensure the availability of vital equipment, improving operational efficiency and patient outcomes.

## Features

- **Real-time Tracking:** Detect and track critical medical equipment in real-time.
- **WebSocket Integration:** Live updates on equipment locations.
- **Geospatial Analysis:** Utilize ArcGIS for spatial analysis and visualization.
- **Machine Learning:** Implement YOLOv3 Tiny for accurate object detection.

## Architecture

- **Frontend:** ArcGIS Maps SDK for JavaScript, Vector Tile Feature Service
- **Backend:** FastAPI, WebSocket for real-time communication
- **Machine Learning:** YOLOv3 Tiny API for object detection
- **Programming Languages:** Python (backend and ML), JavaScript (frontend)

## Installation

### Backend

- [Backend Setup](./backend/README.md)

### Frontend

- [Frontend Setup](./frontend/readme.md)

## WebSocket Integration

The WebSocket server runs on `ws://localhost:8000/ws`. Connect to this endpoint to receive real-time updates of asset locations.

### Example WebSocket Client

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

ws.onopen = function () {
  console.log("WebSocket connection established");
};

ws.onclose = function () {
  console.log("WebSocket connection closed");
};

ws.onerror = function (error) {
  console.error("WebSocket error:", error);
};
```

## Usage

1. **Run object detection and tracking:**

   The `VideoObjectTracker` class is designed to process video streams, detect objects, and send updates via WebSocket.

   ```python
   import asyncio
   from fastapi import FastAPI, WebSocket
   from fastapi.middleware.cors import CORSMiddleware
   from video_object_tracker import VideoObjectTracker
   from fastapi.websockets import WebSocketDisconnect
   import json

   app = FastAPI()

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

   @app.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket):
       global client
       await websocket.accept()
       client = websocket
       try:
           while True:
               directions = ["left", "right", "up", "down"]
               data = {
                   "object_id": int(np.random.default_rng().integers(low=0, high=4, size=1)[0]),
                   "direction": np.random.choice(directions),
               }
               print(data)
               await websocket.send_text(json.dumps(data))
               logging.info(f"Sent data: {data}")
               await asyncio.sleep(3)
       except WebSocketDisconnect:
           client = None

   if __name__ == "__main__":
       import uvicorn
       from threading import Thread

       video_file_path = "path_to_video.mp4"
       model_path = "tiny-yolov3.pt"

       tracker = VideoObjectTracker(video_file_path, model_path, client)

       server_thread = Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000))
       server_thread.start()

       tracker.start_tracking()
   ```

2. **Track assets in real-time:**

   The `VideoObjectTracker` processes video frames, detects objects, and sends updates to the WebSocket client.

   ```python
   import cv2
   import asyncio
   import json
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

       async def send_message_to_websocket(self, message):
           if self.client:
               await self.client.send_text(json.dumps(message))

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
                   obj for obj in new_objects if is_within_distance(coords, obj[2], threshold=20)
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
               if frame_number - self.object_disappear_frame_count[obj[0]] <= 50
           ]
           newObjectPaths = {}
           for obj_id, path in self.object_paths.items():
               if frame_number - self.object_disappear_frame_count[obj_id] <= 50:
                   newObjectPaths[obj_id] = path
               else:
                   dir = checkIfLeftFrame(frame_width, frame_height, path[-1])
                   if not dir:
                       print("did not leave")
                   else:
                       print(dir)
                       # Call WebSocket function to send message
                       message = {
                           "object_id": obj_id,
                           "direction": dir,
                           "path": path,
                           "frame_height": frame_height,
                           "frame_width": frame_width,
                       }
                       asyncio.run(self.send_message_to
   ```

```markdown
\_websocket(message))
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
               frames_per_second=30,
               log_progress=True,
               minimum_percentage_probability=30,
               per_frame_function=self.for_frame,
               return_detected_frame=True,
           )
```

## Future Enhancements

- Enhance model accuracy for better tracking across multiple frames.
- Improve integration with ArcGIS for more advanced spatial analysis.
- Develop more robust WebSocket handling for uninterrupted real-time updates.

## Contributors

- [danieljcohen](https://github.com/danieljcohen)
- [100sun](https://github.com/100sun)

## References

- [Cisco SPACES (2023)](https://spaces.cisco.com/healthcare-asset-tracking-to-improve-efficiency-patient-care)
- [Nuvara (2023)](https://nuvara.com/crash-cart-checks-making-a-plan)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

This revised README provides a more tech-savvy and concise overview of the ArcGIS Care project, focusing on its technical aspects and providing clear instructions for setup and usage.
```
