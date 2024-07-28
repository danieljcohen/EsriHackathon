import json
import logging
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
import numpy as np  # Corrected import

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global client
    await websocket.accept()
    client = websocket
    try:
        # while True:
        # directions = ["left", "right", "up", "down"]
        # data = {
        #     "object_id": int(
        #         np.random.default_rng().integers(low=0, high=2, size=1).item()
        #     ),  # Convert to Python int
        #     "direction": np.random.choice(directions),
        # }
        await asyncio.sleep(30)
        data = {"object_id": 0, "direction": "up"}
        await websocket.send_text(json.dumps(data))
        data = {"object_id": 1, "direction": "down"}
        await websocket.send_text(json.dumps(data))
        logging.info(f"Sent data: {data}")
        # await asyncio.sleep(120)
    except WebSocketDisconnect:
        client = None


if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    # video_file_path = r"esrihackathon\src\components\arcgis-asset-tracker\media\MicrosoftTeams-video (12).mp4"
    # model_path = "tiny-yolov3.pt"

    # tracker = VideoObjectTracker(video_file_path, model_path, client)
    # tracker = VideoObjectTracker(model_path, client)

    # Run FastAPI server in a separate thread
    server_thread = Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000))
    server_thread.start()

    # # Start tracking
    # tracker.start_tracking()
