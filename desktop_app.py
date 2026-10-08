import threading
import time
import webview

from app import app

HOST = "127.0.0.1"
PORT = 5000

def run_flask():
    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False,
        threaded=True
    )

if __name__ == "__main__":
    server = threading.Thread(target=run_flask, daemon=True)
    server.start()

    # Give Flask a moment to start before creating the native window.
    time.sleep(1)

    webview.create_window(
        "SkyGuard AI • Team AetherX",
        f"http://{HOST}:{PORT}",
        width=1400,
        height=900,
        min_size=(1000, 650),
        resizable=True,
        text_select=True
    )

    webview.start()
