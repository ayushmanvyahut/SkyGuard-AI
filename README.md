# 🛡️ SkyGuard AI

### AI-Powered Safety Monitoring & Restricted-Zone Detection System

**Team AetherX — Hackathon Prototype**

SkyGuard AI is an AI-assisted safety monitoring prototype that processes webcam/video input, performs object detection with YOLO, checks a configured restricted zone, generates safety alerts, captures evidence snapshots, stores alert history in SQLite, and presents the results through a Flask dashboard.

> **Current scope:** The prototype uses webcam/video input. Drone integration is a future extension.

## ✨ Key Features

- 🎥 Real-time webcam/video monitoring
- 🤖 YOLO-based object detection
- 🚧 Restricted-zone monitoring
- 🚨 Automatic intrusion alerts
- 📸 Alert snapshot capture
- 🗄️ SQLite alert history
- 📊 Flask-based monitoring dashboard
- ▶️ Start/Stop monitoring
- 📹 Recorded-video analysis workflow
- 🎯 People / object detection mode selection
- ⭕ Rectangle / Square / Circle restricted-area selection in the dashboard
- ✅ Human alert verification
- 🖥️ Optional desktop-app presentation using PyWebView
- 🔒 Privacy-conscious design

## 🏗️ Architecture

```text
Camera / Video Input
        ↓
     OpenCV
        ↓
   YOLO Detection
        ↓
Restricted Zone Check
        ↓
   Alert Generation
      ↙       ↘
 Snapshot      SQLite
      ↓          ↓
      └── Flask Dashboard
              ↓
       Human Verification
```

## 📁 Repository Structure

```text
SkyGuard-AI/
├── main.py
├── app.py
├── view_alerts.py
├── desktop_app.py
├── run_skyguard_app.bat
├── requirements.txt
├── desktop_app_requirements.txt
├── README.md
├── .gitignore
├── alerts_placeholder.txt
└── demo/
    └── screenshots/
        ├── live_monitoring.png
        ├── recorded_analysis.png
        └── alert_history.png
```

### Important runtime files

The following are generated locally and are **not committed**:

- `skyguard_alerts.db` — runtime SQLite database
- `alerts/*.jpg|png|webp` — runtime alert snapshots
- `.venv/` — local Python virtual environment
- uploaded/temporary videos
- `.env` / secrets

The `alerts/` directory is created locally by the application when required.

## ⚙️ Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Flask dashboard

```bash
python app.py
```

Open the local dashboard shown by Flask in your browser.

### 4. Run the desktop-style version

```bash
python desktop_app.py
```

Or double-click:

```text
run_skyguard_app.bat
```

## 🤖 YOLO Model

The Python code loads `yolov8n.pt`. If the model file is not already present, the Ultralytics setup may download the required model when it is first requested, depending on the installed Ultralytics version and network availability.

For a hackathon submission, keep large model artifacts out of Git history if repository size becomes an issue; document the model setup clearly instead.

## 🖼️ UI Screenshots

The `demo/screenshots/` folder contains selected dashboard screenshots for documentation and presentation purposes. These are static demo images, not runtime alert data.

## 🔐 Privacy

The system is designed as an AI-assisted safety-monitoring tool. It should not be presented as a facial-recognition or identity-tracking system. Human verification remains part of the alert workflow.

## 🚀 Future Scope

- Drone video integration
- Physical buzzer/LED/ESP32 alert output
- More advanced analytics
- Improved recorded-video analysis
- Notification integrations
- Easier packaged deployment
