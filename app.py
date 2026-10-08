from flask import (
    Flask,
    render_template_string,
    redirect,
    url_for,
    Response,
    send_from_directory,
    request
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

    width: 70%;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;

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


.analysis-panel{background:#172337;border:1px solid #2d3e59;border-radius:12px;padding:22px;margin-bottom:24px}.analysis-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:18px}.video-box{position:relative;background:#020617;border:1px solid #34465f;border-radius:10px;overflow:hidden;margin-top:14px}.video-box video{width:100%;max-height:430px;display:block;object-fit:contain}.draw-canvas{position:absolute;left:0;top:0;width:100%;height:100%;cursor:crosshair}.analysis-hint{color:#94a3b8;font-size:13px;line-height:1.5}.analysis-controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:12px 0}.analysis-controls select,.analysis-controls input{padding:9px;border-radius:7px;border:1px solid #3b4d69;background:#26364e;color:#fff}.analysis-btn{border:0;padding:10px 15px;border-radius:7px;background:#7c3aed;color:#fff;font-weight:bold;cursor:pointer}.analysis-btn:disabled{opacity:.5}.analysis-progress{height:9px;background:#0b1220;border-radius:10px;overflow:hidden;margin-top:12px}.analysis-progress div{height:100%;width:0;background:#38bdf8}.analysis-shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-top:12px}.analysis-shot{background:#101a2b;border:1px solid #30425f;border-radius:8px;overflow:hidden}.analysis-shot img{width:100%;aspect-ratio:16/10;object-fit:cover}.analysis-shot p{font-size:12px;padding:7px;margin:0;color:#cbd5e1}.results-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}.clear-all-btn{border:0;padding:9px 13px;border-radius:7px;background:#dc2626;color:#fff;font-weight:bold;cursor:pointer}.clear-all-btn:hover{background:#b91c1c}.empty-results{grid-column:1/-1;color:#94a3b8;padding:25px 10px;text-align:center;border:1px dashed #3b4d69;border-radius:8px}.result-time{color:#64748b}.date-heading{margin:18px 0 8px;color:#38bdf8;font-weight:bold}@media(max-width:1000px){.analysis-grid{grid-template-columns:1fr}}
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
style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;"
>

<label for="camera_index" style="color:#cbd5e1;font-weight:bold;">
Camera:
</label>

<select
id="camera_index"
name="camera_index"
style="padding:10px 14px;border-radius:7px;border:none;background:#334155;color:white;font-size:14px;"
>
<option value="0" {% if camera_index == 0 %}selected{% endif %}>Camera 1 (Index 0)</option>
<option value="1" {% if camera_index == 1 %}selected{% endif %}>Camera 2 (Index 1)</option>
<option value="2" {% if camera_index == 2 %}selected{% endif %}>Camera 3 (Index 2)</option>
<option value="3" {% if camera_index == 3 %}selected{% endif %}>Camera 4 (Index 3)</option>
<option value="4" {% if camera_index == 4 %}selected{% endif %}>Camera 5 (Index 4)</option>
</select>

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
object detection and 3 restricted zones.
<br>
Choose the webcam from the <strong>Camera</strong> dropdown before starting monitoring.

</div>


</div>


<div class="analysis-grid">
<section class="analysis-panel">
<h2>🎞️ Recorded Video Analysis</h2>
<p class="analysis-hint">Upload a recorded video, choose People or All Objects, select Rectangle, Square or Circle, draw the restricted area, then analyze the complete video. Every new intrusion event is captured as a snapshot and added to Alert History.</p>
<form id="analysisForm" enctype="multipart/form-data">
<div class="analysis-controls"><input type="file" id="recordedVideo" accept="video/*" required><select id="targetMode"><option value="people">People only</option><option value="all">All detected objects</option></select><select id="shapeType"><option value="rectangle">▭ Rectangle</option><option value="square">□ Square</option><option value="circle">○ Circle</option></select><button type="button" class="analysis-btn" id="clearZones">Clear Zones</button></div>
<div class="video-box" id="recordedBox" style="display:none"><video id="recordedPreview" controls></video><canvas id="drawCanvas" class="draw-canvas"></canvas></div>
<p class="analysis-hint" id="zoneMessage">Select a video, then draw one or more restricted areas.</p>
<button class="analysis-btn" id="analyzeBtn" disabled>🤖 Analyze Recorded Video</button>
</form><div class="analysis-progress"><div id="analysisBar"></div></div><p class="analysis-hint" id="analysisStatus">Waiting for video...</p>
</section>
<section class="analysis-panel">
<div class="results-head"><div><h2>📸 Recorded Results</h2><p class="analysis-hint">Snapshots generated from the selected restricted area stay here after analysis.</p></div>{% if recorded_results %}<form method="POST" action="{{ url_for('clear_recorded_results') }}" onsubmit="return confirm('Clear all recorded results?');"><button type="submit" class="clear-all-btn">🗑 Clear All</button></form>{% endif %}</div>
<div class="analysis-shots" id="analysisShots">
{% for s in recorded_results %}
<div class="analysis-shot"><a href="{{ url_for('recorded_snapshot', filename=s.filename) }}" target="_blank"><img src="{{ url_for('recorded_snapshot', filename=s.filename) }}" alt="Recorded detection"></a><p><b>{{ s.label|capitalize }}</b> • {{ s.confidence }}%<br>Frame {{ s.frame }} • {{ s.time }}s<br><span class="result-time">{{ s.event_time }}</span></p></div>
{% else %}
<div class="empty-results">No recorded results yet. Analyze a video to generate snapshots.</div>
{% endfor %}
</div></section>
</div>

<!-- ================================= -->
<!-- ALERT HISTORY -->
<!-- ================================= -->


<div class="panel">


<h2>
🚨 Alert History
</h2>


{% if alert_groups %}
{% for day, day_alerts in alert_groups.items() %}
<div class="date-heading">📅 {{ day }}</div>
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


{% for a in day_alerts %}


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
{% endfor %}

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


<script>
const rv=document.getElementById('recordedVideo'), pv=document.getElementById('recordedPreview'), rb=document.getElementById('recordedBox'), dc=document.getElementById('drawCanvas'), dctx=dc.getContext('2d'), st=document.getElementById('shapeType'), clearZ=document.getElementById('clearZones'), analyze=document.getElementById('analyzeBtn'), zm=document.getElementById('zoneMessage');
let zones=[],drawing=false,sx=0,sy=0,current=null;
function resizeDraw(){if(!pv.videoWidth)return;dc.width=pv.clientWidth;dc.height=pv.clientHeight;redraw()} function getPos(e){const r=dc.getBoundingClientRect();return{x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height}} function paint(z,active=false){const x=z.x*dc.width,y=z.y*dc.height,w=z.w*dc.width,h=z.h*dc.height;dctx.strokeStyle=active?'#38bdf8':'#ff3b30';dctx.lineWidth=3;dctx.fillStyle='rgba(255,59,48,.12)';if(z.type==='circle'){dctx.beginPath();dctx.ellipse(x+w/2,y+h/2,w/2,h/2,0,0,Math.PI*2);dctx.fill();dctx.stroke()}else{dctx.fillRect(x,y,w,h);dctx.strokeRect(x,y,w,h)}dctx.fillStyle='#fff';dctx.font='bold 13px Arial';dctx.fillText('RESTRICTED',x+6,y+17)} function redraw(){dctx.clearRect(0,0,dc.width,dc.height);zones.forEach(z=>paint(z));if(current)paint(current,true)}
dc.addEventListener('pointerdown',e=>{drawing=true;const p=getPos(e);sx=p.x;sy=p.y;current={type:st.value,x:sx,y:sy,w:0,h:0};dc.setPointerCapture(e.pointerId)});dc.addEventListener('pointermove',e=>{if(!drawing)return;const p=getPos(e);let w=p.x-sx,h=p.y-sy;if(st.value==='square'){const q=Math.max(Math.abs(w),Math.abs(h));w=w<0?-q:q;h=h<0?-q:q}current={type:st.value,x:w<0?p.x:sx,y:h<0?p.y:sy,w:Math.abs(w),h:Math.abs(h)};redraw()});dc.addEventListener('pointerup',()=>{drawing=false;if(current&&current.w>.03&&current.h>.03){zones.push(current);analyze.disabled=false;zm.textContent=zones.length+' restricted zone(s) selected.'}current=null;redraw()});
rv.addEventListener('change',()=>{if(!rv.files[0])return;zones=[];analyze.disabled=true;zm.textContent='Draw restricted areas on the video.';pv.src=URL.createObjectURL(rv.files[0]);rb.style.display='block';pv.addEventListener('loadedmetadata',resizeDraw,{once:true})});window.addEventListener('resize',resizeDraw);clearZ.addEventListener('click',()=>{zones=[];current=null;analyze.disabled=true;redraw();zm.textContent='No restricted zone selected.'});
async function pollAnalysis(){const r=await fetch('/analysis_status');const d=await r.json();document.getElementById('analysisBar').style.width=d.progress+'%';document.getElementById('analysisStatus').textContent=d.message;if(d.snapshots){const g=document.getElementById('analysisShots');g.innerHTML=d.snapshots.map(s=>`<div class="analysis-shot"><a href="/recorded_snapshot/${s.filename}" target="_blank"><img src="/recorded_snapshot/${s.filename}"></a><p><b>${s.label}</b> • ${s.confidence}%<br>Frame ${s.frame} • ${s.time}s</p></div>`).join('')}if(d.status==='complete'||d.status==='error'){clearInterval(window.analysisTimer);analyze.disabled=false;}}
document.getElementById('analysisForm').addEventListener('submit',async e=>{e.preventDefault();if(!rv.files[0]||!zones.length)return;analyze.disabled=true;document.getElementById('analysisStatus').textContent='Uploading video and starting AI analysis...';const fd=new FormData();fd.append('video',rv.files[0]);fd.append('target_mode',document.getElementById('targetMode').value);fd.append('zones',JSON.stringify(zones));const r=await fetch('/analyze_video',{method:'POST',body:fd});const d=await r.json();document.getElementById('analysisStatus').textContent=d.message;if(d.ok)window.analysisTimer=setInterval(pollAnalysis,800)});
</script></body>

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
            WHERE event NOT LIKE '%detected in recorded video'
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
    camera_index = getattr(main, "camera_index", 0)
    recorded_results = main.get_recorded_results()

    alert_groups = {}
    for alert in alerts:
        day = str(alert[2]).split(" ")[0]
        alert_groups.setdefault(day, []).append(alert)


    return render_template_string(

        HTML,

        alerts=alerts,

        total=total,

        pending=pending,

        verified=verified,

        monitoring=monitoring,
        camera_index=camera_index,
        alert_groups=alert_groups,
        recorded_results=recorded_results

    )


# ==========================================
# START MONITORING
# ==========================================

@app.route(
    "/start",
    methods=["POST"]
)

def start_monitoring():

    camera_index = request.form.get("camera_index", "0")

    try:
        camera_index = int(camera_index)
    except ValueError:
        camera_index = 0

    main.start_camera(camera_index)

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
# RECORDED VIDEO ANALYSIS ROUTES
# ==========================================

@app.route("/analyze_video", methods=["POST"])
def analyze_video():
    video = request.files.get("video")
    zones_json = request.form.get("zones", "[]")
    target_mode = request.form.get("target_mode", "people")
    if not video or not video.filename:
        return {"ok": False, "message": "Please select a video."}, 400
    try:
        import json
        zones = json.loads(zones_json)
        if not zones: raise ValueError("Please draw at least one restricted zone.")
    except Exception as e:
        return {"ok": False, "message": str(e)}, 400
    safe_name=os.path.basename(video.filename).replace(" ","_")
    stamp=main.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path=os.path.join(main.UPLOAD_DIR,f"{stamp}_{safe_name}")
    video.save(path)
    main.start_recorded_analysis(path,zones,target_mode)
    return {"ok": True, "message": "Recorded video analysis started."}

@app.route("/analysis_status")
def analysis_status():
    return main.get_analysis_state()

@app.route("/recorded_snapshot/<path:filename>")
def recorded_snapshot(filename):
    return send_from_directory(main.SNAPSHOT_DIR, filename)


# ==========================================
# CLEAR RECORDED RESULTS
# ==========================================

@app.route("/clear_recorded_results", methods=["POST"])
def clear_recorded_results():
    main.clear_recorded_results()
    return redirect(url_for("dashboard"))


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