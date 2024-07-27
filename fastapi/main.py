import cv2
import asyncio
import websockets
import json
from imageai.Detection import VideoObjectDetection
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from util import get_center_of_box, is_within_distance, checkIfLeftFrame
from video_object_tracker import VideoObjectTracker

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []


@app.get("/healthz")
async def get():
    return {"Server": "Live"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    video_file_path = r"esrihackathon\src\components\arcgis-asset-tracker\media\MicrosoftTeams-video (1).mp4"
    model_path = "tiny-yolov3.pt"

    tracker = VideoObjectTracker(video_file_path, model_path)

    # Run FastAPI server in a separate thread
    server_thread = Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000))
    server_thread.start()

    # Start tracking
    tracker.start_tracking()
