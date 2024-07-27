import asyncio
from video_object_tracker import VideoObjectTracker

video_file_path = r"esrihackathon\src\components\arcgis-asset-tracker\media\MicrosoftTeams-video (1).mp4"
model_path = "tiny-yolov3.pt"
websocket_url = "ws://localhost:8000/ws"

tracker = VideoObjectTracker(video_file_path, model_path, websocket_url)
tracker.start_tracking()
