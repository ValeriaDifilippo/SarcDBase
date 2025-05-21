from flask import Flask, render_template
import atexit
import multiprocessing
import signal
import sys
from threading import Timer
import webbrowser
from dash_analysis_who import create_dash_analysis_who
from dash_copy_number import create_dash_copy_number

import socket  # Add at the top if not already imported

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Dash apps
create_dash_analysis_who(app)
create_dash_copy_number(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/analysis/overview')
def analysis_overview():
    return render_template('analysis_overview.html')

@app.route('/analysis/who')
def analysis_who():
    return render_template('analysis_who.html')

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/visualization/overview')
def visualization_overview():
    return render_template('visualization_overview.html')

@app.route('/visualization/copy_number')
def copy_number():
    return render_template('copy_number.html')

# ----------------------
# 1. Define handle_exit
# ----------------------
def handle_exit(signal_received, frame):
    print("\nShutting down Flask app gracefully...")
    sys.exit(0)

# ----------------------
# 2. Define cleanup function
# ----------------------
@atexit.register
def cleanup_resources():
    print("Cleaning up resources...")
    for proc in multiprocessing.active_children():
        print(f"Terminating process {proc.name} with PID {proc.pid}")
        proc.terminate()
    multiprocessing.get_start_method()

# ----------------------
# 3. Find free port and run the app
# ----------------------
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

if __name__ == '__main__':
    port = find_free_port()

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    Timer(1, lambda: webbrowser.open_new(f"http://127.0.0.1:{port}/")).start()

    app.run(debug=True, use_reloader=False, port=port)


