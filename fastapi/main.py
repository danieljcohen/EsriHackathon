import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from video_object_tracker import VideoObjectTracker
from fastapi.websockets import WebSocketDisconnect

app = FastAPI()

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global client
    await websocket.accept()
    client = websocket
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        client = None


if __name__ == "__main__":
    # import uvicorn
    # from threading import Thread

    video_file_path = r"esrihackathon\src\components\arcgis-asset-tracker\media\MicrosoftTeams-video (9).mp4"
    model_path = "tiny-yolov3.pt"

    tracker = VideoObjectTracker(video_file_path, model_path, client)

    # Run FastAPI server in a separate thread
    # server_thread = Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000))
    # server_thread.start()

    # Start tracking
    tracker.start_tracking()
