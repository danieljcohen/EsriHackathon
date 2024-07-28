# ArcGIS Care

Real-time inventory tracking tool enhancing efficiency and reducing operational challenges in hospitals.

![webapp](/media/webapp.png)

## Table of Contents

- [ArcGIS Care](#arcgis-care)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Architecture](#architecture)
    - [Frontend](#frontend)
    - [Backend](#backend)
  - [Installation](#installation)
    - [Suggested Functionality viewing](#suggested-functionality-viewing)
    - [Frontend Setup](#frontend-setup)
    - [Backend Setup](#backend-setup)
  - [Future Enhancements](#future-enhancements)
  - [Contributors](#contributors)
  - [References](#references)

## Overview

ArcGIS Care leverages real-time detection and tracking of critical medical equipment, providing hospitals with the tools to monitor and manage resources efficiently. This project integrates machine learning, GIS, and WebSocket technology to ensure the availability of vital equipment, improving operational efficiency and patient outcomes.

- [DevPost]()
- [YouTube Demo Video]()

## Features

- **Real-time Tracking:** Detect and track critical medical equipment in real-time.
- **Machine Learning:** Implement YOLOv3 Tiny for accurate object detection.
- **Seamless Integration:** Combines ArcGIS Maps SDK for spatial analysis and FastAPI for backend communication.

## Architecture

### Frontend

- **Technology:** ArcGIS Maps SDK for JavaScript, Vector Tile Feature Service
- **Functionality:** Displays real-time locations of tracked medical equipment on a map.

### Backend

- **Technology:** FastAPI, WebSocket for real-time communication
- **Machine Learning:** YOLOv3 Tiny API for object detection
- **Programming Languages:** Python (backend and ML), JavaScript (frontend)

## Installation

### Suggested Functionality viewing

1. Clone the repository

2. Install neccessary packages

```sh
pip install -r requirements.txt
```

3. Run [ai.py](./backend/ai.py)

### Frontend Setup

1. Clone the repository.
2. Navigate to the `frontend` directory.
3. Install dependencies and start the development server:

```sh
npm install
npm start
```

### Backend Setup

1. Clone the repository.
2. Navigate to the `backend` directory.
3. Set up a new conda environment and install dependencies:

```sh
conda create -n arcgis-care-env python=3.8
conda activate arcgis-care-env
pip install --no-cache-dir -r requirements.txt
```

4. Start the FastAPI server:

```sh
python main.py
```

## Future Enhancements

- **Model Accuracy:** Enhance the model for better tracking across multiple frames.
- **Advanced Spatial Analysis:** Improve integration with ArcGIS for more robust spatial analysis.
- **WebSocket Handling:** Develop more robust WebSocket handling for uninterrupted real-time updates.

## Contributors

- [danieljcohen](https://github.com/danieljcohen)
- [100sun](https://github.com/100sun)
- [Major-League-Gaming](https://github.com/Major-League-Gaming)

## References

- [ImageAI Documentation](https://imageai.readthedocs.io/en/latest/)
- [ArcGIS JavaScript API](https://developers.arcgis.com/javascript/latest/)
