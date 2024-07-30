import json
import logging
import asyncio
from fastapi import FastAPI, WebSocket, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from fastapi.responses import StreamingResponse
import cv2
import time
from yolo import YOLO

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
video_file_path = "../media/two_ppl.mp4"
video_capture = cv2.VideoCapture(video_file_path)
fps = video_capture.get(cv2.CAP_PROP_FPS)
frame_delay = 1 / fps
model_path = "tiny-yolov3.pt"
yolo_detector = YOLO(model_path)


def generate_frames():
    global video_capture
    while True:
        success, frame = video_capture.read()
        if not success:
            video_capture = cv2.VideoCapture(video_file_path)  # Restart the video
            success, frame = video_capture.read()

        processed_frame, detections = yolo_detector.detect_objects(frame)
        ret, buffer = cv2.imencode(".jpg", processed_frame)
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


if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    try:
        server_thread = Thread(
            target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000)
        )
        server_thread.start()
    except Exception as e:
        print(f"Error running FastAPI app: {e}")
    finally:
        video_capture.release()
