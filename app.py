from flask import (
    Flask,
    render_template_string,
    redirect,
    url_for,
    Response,
    send_from_directory
)

import sqlite3
import os
import main


# ==========================================
# SKYGUARD AI - TEAM AETHERX
# ==========================================

app = Flask(__name__)

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "skyguard_alerts.db"
)

SNAPSHOT_DIR = os.path.join(
    os.path.dirname(__file__),
    "alerts"
)

os.makedirs(
    SNAPSHOT_DIR,
    exist_ok=True
)


# ==========================================
# DASHBOARD HTML
# ==========================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<title>SkyGuard AI Dashboard</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1"
>


<style>


* {
    box-sizing: border-box;
}


body {

    margin: 0;

    background: #0f172a;

    color: white;

    font-family: Arial, sans-serif;

}


/* ================================= */
/* HEADER */
/* ================================= */


header {

    padding: 24px 5%;

    background: #1e293b;

    border-bottom:
    1px solid #334155;

}


h1 {

    margin: 0;

    color: #38bdf8;

    font-size: 42px;

}


.subtitle {

    color: #94a3b8;

    margin-top: 8px;

    font-size: 18px;

}


/* ================================= */
/* MAIN */
/* ================================= */


main {

    padding: 28px 5%;

}


/* ================================= */
/* STATISTICS */
/* ================================= */


.cards {

    display: grid;

    grid-template-columns:
    repeat(
        auto-fit,
        minmax(180px, 1fr)
    );

    gap: 18px;

    margin-bottom: 28px;

}


.card {

    background: #1e293b;

    border:
    1px solid #334155;

    border-radius: 12px;

    padding: 22px;

}


.card p {

    color: #94a3b8;

    margin: 0 0 12px;

}


.number {

    font-size: 30px;

    font-weight: bold;

}


.green {

    color: #4ade80;

}


.red {

    color: #f87171;

}


/* ================================= */
/* LIVE PANEL */
/* ================================= */


.live-panel {

    background: #1e293b;

    border:
    1px solid #334155;

    border-radius: 12px;

    padding: 28px;

    margin-bottom: 32px;

}


.live-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    flex-wrap: wrap;

    gap: 15px;

}


.live-header h2 {

    margin: 0;

    font-size: 28px;

}


.live-status {

    padding: 9px 16px;

    border-radius: 20px;

    font-size: 14px;

    font-weight: bold;

}


.active {

    background: #065f46;

    color: #6ee7b7;

}


.inactive {

    background: #450a0a;

    color: #fca5a5;

}


/* ================================= */
/* CONTROL BUTTONS */
/* ================================= */


.control-buttons {

    margin-top: 20px;

    display: flex;

    gap: 12px;

    flex-wrap: wrap;

}


button {

    border: none;

    padding: 10px 17px;

    border-radius: 7px;

    color: white;

    font-size: 14px;

    font-weight: bold;

    cursor: pointer;

}


.start-btn {

    background: #16a34a;

}


.start-btn:hover {

    background: #15803d;

}


.stop-btn {

    background: #dc2626;

}


.stop-btn:hover {

    background: #b91c1c;

}


.verify-btn {

    background: #0284c7;

}


.verify-btn:hover {

    background: #0369a1;

}


/* ================================= */
/* CAMERA */
/* ================================= */


.camera-container {

    margin-top: 22px;

    width: 100%;

    background: #020617;

    border-radius: 10px;

    overflow: hidden;

    border:
    2px solid #334155;

}


.camera-container img {

    width: 100%;

    display: block;

}


.camera-off {

    min-height: 420px;

    display: flex;

    align-items: center;

    justify-content: center;

    flex-direction: column;

    color: #64748b;

    text-align: center;

}


.camera-off .icon {

    font-size: 60px;

    margin-bottom: 15px;

}


.camera-info {

    color: #94a3b8;

    margin-top: 14px;

    font-size: 15px;

}


/* ================================= */
/* ALERT HISTORY */
/* ================================= */


.panel {

    background: #1e293b;

    border:
    1px solid #334155;

    border-radius: 12px;

    padding: 22px;

}


table {

    width: 100%;

    border-collapse: collapse;

    min-width: 900px;

}


th,
td {

    text-align: left;

    padding: 14px 10px;

    border-bottom:
    1px solid #334155;

}


th {

    color: #94a3b8;

}


.table-wrap {

    overflow-x: auto;

}


/* ================================= */
/* STATUS */
/* ================================= */


.status {

    padding: 6px 10px;

    border-radius: 20px;

    font-size: 12px;

    background: #422006;

    color: #fbbf24;

}


.verified {

    background: #064e3b;

    color: #6ee7b7;

}


/* ================================= */
/* SNAPSHOT BUTTON */
/* ================================= */


.snapshot-btn {

    display: inline-block;

    background: #7c3aed;

    color: white;

    padding: 7px 12px;

    border-radius: 6px;

    text-decoration: none;

    font-size: 13px;

    font-weight: bold;

}


.snapshot-btn:hover {

    background: #6d28d9;

}


.no-snapshot {

    color: #64748b;

    font-size: 13px;

}


/* ================================= */
/* FOOTER */
/* ================================= */


footer {

    text-align: center;

    color: #64748b;

    padding: 24px;

}


</style>

</head>


<body>


<!-- ================================= -->
<!-- HEADER -->
<!-- ================================= -->


<header>

<h1>
🛡️ SkyGuard AI
</h1>


<div class="subtitle">

AI-Powered Safety Monitoring Dashboard

</div>

</header>


<main>


<!-- ================================= -->
<!-- STATISTICS -->
<!-- ================================= -->


<div class="cards">


<div class="card">

<p>
Total Alerts
</p>

<div class="number">

{{ total }}

</div>

</div>


<div class="card">

<p>
Pending Verification
</p>

<div class="number red">

{{ pending }}

</div>

</div>


<div class="card">

<p>
Verified Alerts
</p>

<div class="number green">

{{ verified }}

</div>

</div>


<div class="card">

<p>
Monitoring
</p>

<div class="number
{% if monitoring %}
green
{% else %}
red
{% endif %}
">

{% if monitoring %}

ACTIVE

{% else %}

OFF

{% endif %}

</div>

</div>


</div>


<!-- ================================= -->
<!-- LIVE MONITORING -->
<!-- ================================= -->


<div class="live-panel">


<div class="live-header">


<h2>
📹 Live AI Monitoring
</h2>


<div class="live-status
{% if monitoring %}
active
{% else %}
inactive
{% endif %}
">


{% if monitoring %}

🟢 LIVE • YOLO AI Monitoring Active

{% else %}

🔴 MONITORING OFF

{% endif %}


</div>


</div>


<!-- ================================= -->
<!-- CONTROL BUTTONS -->
<!-- ================================= -->


<div class="control-buttons">


<form
method="POST"
action="{{ url_for('start_monitoring') }}"
>


<button
class="start-btn"
type="submit"
>

▶ Start Monitoring

</button>


</form>


<form
method="POST"
action="{{ url_for('stop_monitoring') }}"
>


<button
class="stop-btn"
type="submit"
>

■ Stop Monitoring

</button>


</form>


</div>


<!-- ================================= -->
<!-- CAMERA -->
<!-- ================================= -->


<div class="camera-container">


{% if monitoring %}


<img
src="{{ url_for('video_feed') }}"
alt="SkyGuard AI Live Camera"
>


{% else %}


<div class="camera-off">


<div class="icon">

📷

</div>


<h3>

Camera Monitoring is OFF

</h3>


<p>

Dashboard is running normally.

<br>

Click
<strong>
"Start Monitoring"
</strong>
to activate AI camera.

</p>


</div>


{% endif %}


</div>


<div class="camera-info">

Real-time camera feed with AI-based
person detection and restricted-zone monitoring.

</div>


</div>


<!-- ================================= -->
<!-- ALERT HISTORY -->
<!-- ================================= -->


<div class="panel">


<h2>
🚨 Alert History
</h2>


{% if alerts %}


<div class="table-wrap">


<table>


<thead>


<tr>

<th>
ID
</th>

<th>
Event
</th>

<th>
Date & Time
</th>

<th>
Snapshot
</th>

<th>
Status
</th>

<th>
Action
</th>

</tr>


</thead>


<tbody>


{% for a in alerts %}


<tr>


<!-- ID -->


<td>

{{ a[0] }}

</td>


<!-- EVENT -->


<td>

{{ a[1] }}

</td>


<!-- TIME -->


<td>

{{ a[2] }}

</td>


<!-- SNAPSHOT -->


<td>


{% if a[4] %}


<a
class="snapshot-btn"
href="{{ url_for(
    'snapshot',
    filename=a[4]
) }}"
target="_blank"
>

📸 View

</a>


{% else %}


<span class="no-snapshot">

No Snapshot

</span>


{% endif %}


</td>


<!-- STATUS -->


<td>


<span
class="status
{% if a[3] == 'Verified' %}
verified
{% endif %}
"
>

{{ a[3] }}

</span>


</td>


<!-- ACTION -->


<td>


{% if a[3] == "Pending" %}


<form
method="POST"
action="{{ url_for(
    'verify',
    alert_id=a[0]
) }}"
>


<button
class="verify-btn"
type="submit"
>

Mark Verified

</button>


</form>


{% else %}


<span class="green">

✓ Done

</span>


{% endif %}


</td>


</tr>


{% endfor %}


</tbody>


</table>


</div>


{% else %}


<p>

No alerts recorded yet.

</p>


{% endif %}


</div>


</main>


<footer>

Team AetherX
|
Beyond Vision, Beyond Limits

</footer>


</body>

</html>

"""


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    return sqlite3.connect(
        DB_PATH
    )


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/")
def dashboard():

    alerts = []


    if os.path.exists(DB_PATH):

        conn = get_connection()

        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT
                id,
                event,
                event_time,
                status,
                snapshot
            FROM alerts
            ORDER BY id DESC
            """
        )


        alerts = cursor.fetchall()

        conn.close()


    # Statistics

    total = len(alerts)


    pending = sum(
        1
        for a in alerts
        if a[3] == "Pending"
    )


    verified = sum(
        1
        for a in alerts
        if a[3] == "Verified"
    )


    monitoring = main.is_camera_running()


    return render_template_string(

        HTML,

        alerts=alerts,

        total=total,

        pending=pending,

        verified=verified,

        monitoring=monitoring

    )


# ==========================================
# START MONITORING
# ==========================================

@app.route(
    "/start",
    methods=["POST"]
)

def start_monitoring():

    main.start_camera()

    return redirect(
        url_for("dashboard")
    )


# ==========================================
# STOP MONITORING
# ==========================================

@app.route(
    "/stop",
    methods=["POST"]
)

def stop_monitoring():

    main.stop_camera()

    return redirect(
        url_for("dashboard")
    )


# ==========================================
# LIVE VIDEO STREAM
# ==========================================

@app.route(
    "/video_feed"
)

def video_feed():

    return Response(

        main.generate_frames(),

        mimetype=
        "multipart/x-mixed-replace; boundary=frame"

    )


# ==========================================
# SNAPSHOT VIEW
# ==========================================

@app.route(
    "/snapshot/<filename>"
)

def snapshot(filename):

    return send_from_directory(

        SNAPSHOT_DIR,

        filename

    )


# ==========================================
# VERIFY ALERT
# ==========================================

@app.route(
    "/verify/<int:alert_id>",
    methods=["POST"]
)

def verify(alert_id):

    if os.path.exists(DB_PATH):

        conn = get_connection()

        cursor = conn.cursor()


        cursor.execute(

            """
            UPDATE alerts

            SET status = ?

            WHERE id = ?

            AND status = ?
            """,

            (
                "Verified",
                alert_id,
                "Pending"
            )

        )


        conn.commit()

        conn.close()


    return redirect(
        url_for("dashboard")
    )


# ==========================================
# START FLASK
# ==========================================

if __name__ == "__main__":

    print("")
    print("======================================")
    print("     SKYGUARD AI DASHBOARD")
    print("======================================")
    print("")
    print(
        "Dashboard: http://127.0.0.1:5000"
    )
    print("")

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False,

        threaded=True

    )