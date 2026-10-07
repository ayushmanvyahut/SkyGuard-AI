import cv2
import sqlite3
import threading
import time
import os
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


# ==========================================
# ALERT TRACKING
# ==========================================

previous_alert = False

clear_frames = 0

CLEAR_THRESHOLD = 15


# ==========================================
# START CAMERA
# ==========================================

def start_camera():

    global cap
    global camera_thread
    global camera_running

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

        # Open webcam
        cap = cv2.VideoCapture(0)

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
        # RESTRICTED ZONE
        # ==================================

        x1 = int(width * 0.60)

        y1 = int(height * 0.20)

        x2 = int(width * 0.95)

        y2 = int(height * 0.90)


        # Draw restricted zone

        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            (0, 0, 255),

            2

        )


        # Zone label

        cv2.putText(

            frame,

            "RESTRICTED ZONE",

            (
                x1,
                max(y1 - 10, 25)
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 0, 255),

            2

        )


        # ==================================
        # YOLO OBJECT DETECTION
        # ==================================

        results = model(

            frame,

            verbose=False

        )


        alert = False


        # ==================================
        # PROCESS DETECTIONS
        # ==================================

        for box in results[0].boxes:

            cls_id = int(
                box.cls[0]
            )

            label = model.names[
                cls_id
            ]

            confidence = float(
                box.conf[0]
            )


            # Detect person only

            if (
                label == "person"
                and
                confidence > 0.5
            ):

                # Bounding box

                bx1, by1, bx2, by2 = map(

                    int,

                    box.xyxy[0]

                )


                # Person center

                cx = (
                    bx1 + bx2
                ) // 2

                cy = (
                    by1 + by2
                ) // 2


                # Check restricted zone

                inside = (

                    x1 <= cx <= x2

                    and

                    y1 <= cy <= y2

                )


                # ==================================
                # PERSON INSIDE ZONE
                # ==================================

                if inside:

                    alert = True

                    color = (
                        0,
                        0,
                        255
                    )


                    cv2.putText(

                        frame,

                        "ZONE ALERT",

                        (
                            bx1,
                            max(
                                by1 - 10,
                                25
                            )
                        ),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.7,

                        color,

                        2

                    )


                else:

                    color = (
                        0,
                        255,
                        0
                    )


                # ==================================
                # PERSON BOUNDING BOX
                # ==================================

                cv2.rectangle(

                    frame,

                    (
                        bx1,
                        by1
                    ),

                    (
                        bx2,
                        by2
                    ),

                    color,

                    2

                )


                # ==================================
                # CONFIDENCE
                # ==================================

                cv2.putText(

                    frame,

                    f"Person {confidence:.2f}",

                    (
                        bx1,
                        min(
                            by2 + 20,
                            height - 5
                        )
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    color,

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

                        "Person detected in restricted zone",

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