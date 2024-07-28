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

## Usage

1. **Run object detection and tracking:**

   The `VideoObjectTracker` class is designed to process video streams, detect objects, and send updates via WebSocket.

2. **Track assets in real-time:**

   The `VideoObjectTracker` processes video frames, detects objects, and sends updates to the WebSocket client.

## Future Enhancements

- Enhance model accuracy for better tracking across multiple frames.
- Improve integration with ArcGIS for more advanced spatial analysis.
- Develop more robust WebSocket handling for uninterrupted real-time updates.

## Contributors

- [danieljcohen](https://github.com/danieljcohen)
- [100sun](https://github.com/100sun)

## References
