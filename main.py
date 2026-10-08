import cv2
import sqlite3
import threading
import time
import os
import winsound
from datetime import datetime
from ultralytics import YOLO

# ==========================================
# SKYGUARD AI - TEAM AETHERX
# ==========================================

print("Starting SkyGuard AI...")

# ==========================================
# YOLO MODEL
# ==========================================

model = YOLO("yolov8n.pt")

# ==========================================
# DATABASE
# ==========================================

DB_PATH = "skyguard_alerts.db"

# ==========================================
# SNAPSHOT DIRECTORY
# ==========================================

SNAPSHOT_DIR = "alerts"

os.makedirs(
    SNAPSHOT_DIR,
    exist_ok=True
)


# ==========================================
# CREATE / UPDATE DATABASE
# ==========================================

def create_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            event_time TEXT NOT NULL,
            status TEXT NOT NULL,
            snapshot TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recorded_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_time TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            frame_no INTEGER NOT NULL,
            video_time REAL NOT NULL,
            snapshot TEXT NOT NULL
        )
    """)

    # Check existing columns
    cursor.execute(
        "PRAGMA table_info(alerts)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    # Add snapshot column to old database
    if "snapshot" not in columns:

        cursor.execute(
            """
            ALTER TABLE alerts
            ADD COLUMN snapshot TEXT
            """
        )

        print(
            "Database updated: snapshot column added."
        )

    conn.commit()

    conn.close()


create_database()


# ==========================================
# CAMERA VARIABLES
# ==========================================

cap = None

camera_thread = None

camera_running = False

latest_frame = None

frame_lock = threading.Lock()

camera_lock = threading.Lock()

# Selected webcam index from the dashboard.
camera_index = 0


# ==========================================
# CONTINUOUS AUDIO ALARM
# ==========================================

alarm_stop_event = threading.Event()
alarm_thread = None

def _alarm_loop():
    while not alarm_stop_event.is_set():
        try:
            winsound.Beep(1400, 300)
            if alarm_stop_event.wait(0.10): break
            winsound.Beep(900, 300)
            if alarm_stop_event.wait(0.10): break
        except Exception as e:
            print('Audio alarm error:', e)
            break

def start_alarm():
    global alarm_thread
    if alarm_thread and alarm_thread.is_alive(): return
    alarm_stop_event.clear()
    alarm_thread = threading.Thread(target=_alarm_loop, daemon=True)
    alarm_thread.start()

def stop_alarm():
    alarm_stop_event.set()


# ==========================================
# ALERT TRACKING
# ==========================================

previous_alert = False

clear_frames = 0

CLEAR_THRESHOLD = 15


# ==========================================
# START CAMERA
# ==========================================

def start_camera(selected_camera=0):

    global cap
    global camera_thread
    global camera_running
    global camera_index

    with camera_lock:

        # Already running
        if camera_running:

            print(
                "Camera is already running."
            )

            return True

        print(
            "Starting camera..."
        )

        # Open selected webcam
        camera_index = int(selected_camera)
        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():

            print(
                "Error: Camera could not be opened!"
            )

            cap.release()

            cap = None

            return False

        camera_running = True

        # Start background thread
        camera_thread = threading.Thread(
            target=camera_loop,
            daemon=True
        )

        camera_thread.start()

        print(
            "Camera started successfully!"
        )

        print(
            "AI camera processing started..."
        )

        return True


# ==========================================
# CAMERA PROCESSING LOOP
# ==========================================

def camera_loop():

    global latest_frame

    global previous_alert

    global clear_frames

    global camera_running

    while camera_running:

        # Check camera
        if cap is None:

            break

        # Read frame
        ret, frame = cap.read()

        if not ret:

            print(
                "Error: Could not read camera frame."
            )

            time.sleep(0.1)

            continue

        # Frame dimensions
        height, width = frame.shape[:2]


        # ==================================
        # THREE RESTRICTED ZONES
        # ==================================

        zones = [
            ("RESTRICTED ZONE 1", int(width * 0.58), int(height * 0.08),
             int(width * 0.96), int(height * 0.36)),
            ("RESTRICTED ZONE 2", int(width * 0.58), int(height * 0.38),
             int(width * 0.96), int(height * 0.66)),
            ("RESTRICTED ZONE 3", int(width * 0.58), int(height * 0.68),
             int(width * 0.96), int(height * 0.94)),
        ]

        for zone_name, zx1, zy1, zx2, zy2 in zones:
            cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 0, 255), 2)
            cv2.putText(
                frame, zone_name, (zx1, max(zy1 - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2
            )

        # ==================================
        # YOLO OBJECT DETECTION
        # ==================================

        results = model(frame, verbose=False)
        alert = False
        alert_event = "Object detected in restricted zone"

        # ==================================
        # PROCESS ALL DETECTED OBJECTS
        # ==================================

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            confidence = float(box.conf[0])

            if confidence < 0.40:
                continue

            bx1, by1, bx2, by2 = map(int, box.xyxy[0])
            cx = (bx1 + bx2) // 2
            cy = (by1 + by2) // 2

            inside_zone = False
            zone_hit = ""

            for zone_name, zx1, zy1, zx2, zy2 in zones:
                if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                    inside_zone = True
                    zone_hit = zone_name
                    break

            # Any detected object inside any restricted zone triggers the alert.
            if inside_zone:
                alert = True
                alert_event = f"{label.capitalize()} detected in {zone_hit}"
                box_color = (0, 0, 255)
            else:
                box_color = (0, 255, 0)

            cv2.rectangle(
                frame, (bx1, by1), (bx2, by2), box_color, 2
            )

            cv2.putText(
                frame,
                f"{label} {confidence:.0%}",
                (bx1, max(by1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                box_color,
                2
            )

            if inside_zone:
                cv2.putText(
                    frame,
                    f"ZONE ALERT: {label.upper()}",
                    (bx1, min(by2 + 22, height - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

        # ==================================
        # ALERT HANDLING
        # ==================================

        if alert:

            # Reset clear frames

            clear_frames = 0


            # New intrusion
            if not previous_alert:

                # Current time

                event_time = datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                )


                # Keep alarm active for the entire intrusion.
                start_alarm()

                # ==================================
                # SNAPSHOT
                # ==================================

                snapshot_name = (

                    "alert_"

                    +

                    datetime.now().strftime(

                        "%Y%m%d_%H%M%S_%f"

                    )

                    +

                    ".jpg"

                )


                snapshot_path = os.path.join(

                    SNAPSHOT_DIR,

                    snapshot_name

                )


                # Save current frame

                snapshot_saved = cv2.imwrite(

                    snapshot_path,

                    frame

                )


                if snapshot_saved:

                    print(
                        "📸 SNAPSHOT SAVED:",
                        snapshot_name
                    )

                else:

                    print(
                        "⚠️ Snapshot could not be saved."
                    )

                    snapshot_name = None


                # ==================================
                # SAVE ALERT TO DATABASE
                # ==================================

                conn = sqlite3.connect(
                    DB_PATH
                )

                cursor = conn.cursor()


                cursor.execute(

                    """
                    INSERT INTO alerts
                    (
                        event,
                        event_time,
                        status,
                        snapshot
                    )

                    VALUES (?, ?, ?, ?)
                    """,

                    (

                        alert_event,

                        event_time,

                        "Pending",

                        snapshot_name

                    )

                )


                conn.commit()

                conn.close()


                print(
                    "🚨 ALERT SAVED:",
                    event_time
                )


            # Mark alert active

            previous_alert = True


        # ==================================
        # NO ALERT
        # ==================================

        else:

            if previous_alert:

                clear_frames += 1


                # Reset after clear frames

                if (
                    clear_frames
                    >=
                    CLEAR_THRESHOLD
                ):

                    previous_alert = False

                    clear_frames = 0
                    stop_alarm()


                    print(

                        "Zone clear. "
                        "Monitoring resumed."

                    )


        # ==================================
        # TOP STATUS BAR
        # ==================================

        if alert:

            # Red warning bar

            cv2.rectangle(

                frame,

                (0, 0),

                (
                    width,
                    45
                ),

                (0, 0, 180),

                -1

            )


            cv2.putText(

                frame,

                "WARNING: RESTRICTED ZONE ALERT",

                (10, 30),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255, 255, 255),

                2

            )


        else:

            # Green status

            cv2.putText(

                frame,

                "STATUS: AREA CLEAR",

                (10, 30),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (0, 200, 0),

                2

            )


        # ==================================
        # SAVE FRAME FOR FLASK
        # ==================================

        with frame_lock:

            latest_frame = frame.copy()


# ==========================================
# RECORDED VIDEO ANALYSIS
# ==========================================

analysis_lock = threading.Lock()
analysis_state = {"status":"idle","progress":0,"message":"No video selected.","snapshots":[],"total_detections":0}
UPLOAD_DIR = "uploads"
VIDEO_SNAPSHOT_DIR = os.path.join(SNAPSHOT_DIR, "recorded")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VIDEO_SNAPSHOT_DIR, exist_ok=True)

def get_analysis_state():
    with analysis_lock: return dict(analysis_state)

def _inside_zone(cx, cy, z):
    try:
        kind=z.get("type","rectangle"); x=float(z.get("x",0)); y=float(z.get("y",0)); w=float(z.get("w",0)); h=float(z.get("h",0))
        if kind in ("rectangle","square"): return x<=cx<=x+w and y<=cy<=y+h
        r=max(w,h)/2; mx=x+w/2; my=y+h/2
        return (cx-mx)**2+(cy-my)**2 <= r*r
    except Exception: return False

def analyze_recorded_video(video_path, zones, target_mode="people"):
    cap_local = None
    snapshots = []
    captured_ids = set()
    fallback_active = False
    clear_count = 0
    try:
        with analysis_lock:
            analysis_state.update(
                status="processing",
                progress=0,
                message="Opening recorded video...",
                snapshots=[],
                total_detections=0
            )

        cap_local = cv2.VideoCapture(video_path)
        if not cap_local.isOpened():
            raise RuntimeError("Recorded video could not be opened.")

        total = int(cap_local.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap_local.get(cv2.CAP_PROP_FPS) or 25)
        frame_no = 0

        while True:
            ok, frame = cap_local.read()
            if not ok:
                break

            frame_no += 1
            height, width = frame.shape[:2]

            # Tracking gives individual people/objects a temporary ID so
            # multiple people entering the same zone can produce separate snapshots.
            results = model.track(frame, persist=True, verbose=False)
            hits = []

            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                confidence = float(box.conf[0])

                if confidence < 0.40:
                    continue
                if target_mode == "people" and label != "person":
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = ((x1 + x2) / 2) / width
                cy = ((y1 + y2) / 2) / height

                if any(_inside_zone(cx, cy, z) for z in zones):
                    track_id = None
                    if box.id is not None:
                        try:
                            track_id = int(box.id[0])
                        except Exception:
                            track_id = None
                    hits.append((label, confidence, x1, y1, x2, y2, track_id))

            new_hits = []
            for hit in hits:
                track_id = hit[6]
                if track_id is not None:
                    if track_id not in captured_ids:
                        captured_ids.add(track_id)
                        new_hits.append(hit)
                elif not fallback_active:
                    new_hits.append(hit)
                    fallback_active = True

            if not hits:
                clear_count += 1
                if clear_count >= 8:
                    fallback_active = False
                    clear_count = 0
            else:
                clear_count = 0

            for label, confidence, x1, y1, x2, y2, track_id in new_hits:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                fn = f"recorded_{stamp}_frame{frame_no}.jpg"
                rel = "recorded/" + fn
                out = os.path.join(VIDEO_SNAPSHOT_DIR, fn)

                annotated = frame.copy()
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(
                    annotated,
                    f"{label} {confidence:.0%} - RESTRICTED ZONE",
                    (x1, max(y1 - 12, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 0, 255),
                    2
                )
                cv2.imwrite(out, annotated)

                event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO recorded_results
                    (event_time,label,confidence,frame_no,video_time,snapshot)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        event_time,
                        label,
                        float(confidence),
                        int(frame_no),
                        round(frame_no / fps, 2),
                        rel
                    )
                )
                conn.commit()
                conn.close()

                snapshots.append({
                    "filename": rel,
                    "label": label,
                    "confidence": round(confidence * 100),
                    "frame": frame_no,
                    "time": round(frame_no / fps, 2),
                    "track_id": track_id
                })

                with analysis_lock:
                    analysis_state.update(
                        snapshots=list(snapshots),
                        total_detections=len(snapshots)
                    )

            progress = min(100, int(frame_no * 100 / total)) if total else 0
            with analysis_lock:
                analysis_state.update(
                    progress=progress,
                    message=f"Analyzing frame {frame_no}..."
                )

        with analysis_lock:
            analysis_state.update(
                status="complete",
                progress=100,
                message=f"Analysis complete. {len(snapshots)} incident snapshot(s) found.",
                snapshots=snapshots,
                total_detections=len(snapshots)
            )

    except Exception as e:
        with analysis_lock:
            analysis_state.update(
                status="error",
                message=str(e),
                progress=0
            )
    finally:
        if cap_local:
            cap_local.release()

def get_recorded_results():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id,event_time,label,confidence,frame_no,video_time,snapshot
        FROM recorded_results
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "event_time": r[1], "label": r[2],
            "confidence": round(r[3] * 100), "frame": r[4],
            "time": r[5], "filename": r[6]
        }
        for r in rows
    ]

def clear_recorded_results():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT snapshot FROM recorded_results")
    files = [r[0] for r in cur.fetchall()]
    # Also remove legacy recorded-video alerts created by older versions.
    cur.execute("SELECT snapshot FROM alerts WHERE event LIKE '%detected in recorded video'")
    legacy_files = [r[0] for r in cur.fetchall() if r[0]]
    cur.execute("DELETE FROM recorded_results")
    cur.execute("DELETE FROM alerts WHERE event LIKE '%detected in recorded video'")
    conn.commit()
    conn.close()

    for rel in files + legacy_files:
        try:
            path = os.path.join(SNAPSHOT_DIR, *rel.replace("\\", "/").split("/"))
            if os.path.isfile(path):
                os.remove(path)
        except OSError:
            pass

    # Clean any remaining files produced by recorded analysis.
    try:
        for name in os.listdir(VIDEO_SNAPSHOT_DIR):
            path = os.path.join(VIDEO_SNAPSHOT_DIR, name)
            if os.path.isfile(path):
                os.remove(path)
    except OSError:
        pass

    with analysis_lock:
        analysis_state.update(
            status="idle", progress=0,
            message="Recorded results cleared.",
            snapshots=[], total_detections=0
        )

def start_recorded_analysis(video_path,zones,target_mode="people"):
    threading.Thread(target=analyze_recorded_video,args=(video_path,zones,target_mode),daemon=True).start()


# ==========================================
# STOP CAMERA
# ==========================================

def stop_camera():

    global cap

    global camera_running

    global latest_frame

    global previous_alert

    global clear_frames


    with camera_lock:

        if not camera_running:

            return


        print(
            "Stopping camera..."
        )


        # Stop processing loop

        camera_running = False


        # Give thread time to stop

        time.sleep(0.2)


        # Release camera

        if cap is not None:

            cap.release()

            cap = None


        # Clear frame

        with frame_lock:

            latest_frame = None


        # Reset alert state

        previous_alert = False

        clear_frames = 0
        stop_alarm()


        print(
            "Camera stopped."
        )


# ==========================================
# CAMERA STATUS
# ==========================================

def is_camera_running():

    return camera_running


# ==========================================
# LIVE VIDEO STREAM
# ==========================================

def generate_frames():

    while True:

        # Camera OFF

        if not camera_running:

            time.sleep(0.1)

            continue


        # Get latest frame

        with frame_lock:

            if latest_frame is None:

                frame = None

            else:

                frame = latest_frame.copy()


        if frame is None:

            time.sleep(0.05)

            continue


        # Convert frame to JPEG

        success, buffer = cv2.imencode(

            ".jpg",

            frame

        )


        if not success:

            continue


        frame_bytes = buffer.tobytes()


        # Flask MJPEG stream

        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            +

            frame_bytes

            +

            b"\r\n"

        )