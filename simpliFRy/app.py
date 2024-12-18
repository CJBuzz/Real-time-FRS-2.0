import argparse
import json
import signal

from flask import Flask, Response, stream_with_context, render_template, request, redirect, url_for
from flask_cors import CORS

from fr import FRVidPlayer
from utils import log_info

parser = argparse.ArgumentParser(description="Facial Recognition Program")

# Arguments
# parser.add_argument(
#     "stream", type=str, help="URL to origin streaming camera feed"
# )
parser.add_argument(
    "-d",
    "--data",
    type=str,
    help="File path to json file containing data",
    required=False,
)
parser.add_argument(
    "-ip",
    "--ipaddress",
    type=str,
    help="IP address to host the app from",
    required=False,
    default="0.0.0.0",
)
parser.add_argument(
    "-p",
    "--port",
    type=str,
    help="Port to host the app from",
    required=False,
    default="1333",
)

args = parser.parse_args()

app = Flask(__name__)
CORS(app)

log_info("Starting FR Session")

test = FRVidPlayer()
#test.start_stream()

@app.route("/start", methods=["POST"])
def start():
    """API for frontend to start FR"""

    if test.is_started:        
        response_msg = json.dumps({"stream": False, "message": "Stream already started!"})
        return Response(response_msg, status=200, mimetype='application/json')

    stream_src = request.form.get("stream_src", None)
    data_file = request.form.get("data_file", None)

    test.start_stream(stream_src)

    try:
        test.load_embeddings(data_file)
    except (ValueError, FileNotFoundError) as err:
        test.end_event.set()
        response_msg = json.dumps({"stream": False, "message": str(err)})
        return Response(response_msg, status=200, mimetype='application/json')

    test.start_inference()
    response_msg = json.dumps({"stream": True, "message": "Success!"})
    return Response(response_msg, status=200, mimetype='application/json')

@app.route("/checkAlive") 
def check_alive():
    """API to check if FR has started"""

    try:
        if test.streamThread.is_alive():
            response = "Yes"
        else: 
            response = "No"
    except AttributeError: 
        response = "No"

    return Response(response, status=200, mimetype='application/json')

@app.route("/vidFeed")
def video_feed():
    """Returns a HTTP streaming response of the video feed from FFMPEG"""

    return Response(
        test.start_broadcast(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/frResults")
def fr_results():
    """Returns a HTTP streaming response of the recently detected names, their scores, and bounding boxes"""

    return Response(
        test.start_detection_broadcast(), mimetype="application/json"
    )


@app.route("/submit", methods=["POST"])
def submit():
    """Handles form submission to adjust FR settings, subsequently redirects to settings page"""

    new_settings = {
        "threshold": float(request.form.get(
            "threshold", test.fr_settings["threshold"]
        )),
        "holding_time": int(float(
            request.form.get("holding_time", test.fr_settings["holding_time"]))
        ),
        "use_differentiator": "use_differentiator" in request.form,
        "threshold_lenient_diff": float(request.form.get(
            "threshold_lenient_diff", test.fr_settings["threshold_lenient_diff"]
        )),
        "similarity_gap": float(request.form.get(
            "similarity_gap", test.fr_settings["similarity_gap"]
        )),
        "use_persistor": "use_persistor" in request.form,
        "threshold_prev": float(request.form.get(
            "threshold_prev", test.fr_settings["threshold_prev"]
        )),
        "threshold_iou": float(request.form.get(
            "threshold_iou", test.fr_settings["threshold_iou"]
        )),
        "threshold_lenient_pers": float(request.form.get(
            "threshold_lenient_pers", test.fr_settings["threshold_lenient_pers"]
        ))
    }

    test.adjust_values(new_settings)
    return redirect(url_for('settings'))


@app.route("/")
def index():
    """Renders home page which includes the live feed (with bounding boxes) and a detection list"""

    return render_template("index.html")


@app.route("/settings")
def settings():
    """Renders settings page"""

    return render_template(
        "settings.html",
        threshold=test.fr_settings["threshold"],
        holding_time=test.fr_settings["holding_time"],
        use_differentiator=test.fr_settings["use_differentiator"],
        threshold_lenient_diff=test.fr_settings["threshold_lenient_diff"],
        similarity_gap=test.fr_settings["similarity_gap"],
        use_persistor=test.fr_settings["use_persistor"],
        threshold_prev=test.fr_settings["threshold_prev"],
        threshold_iou=test.fr_settings["threshold_iou"],
        threshold_lenient_pers=test.fr_settings["threshold_lenient_pers"],
    )


if __name__ == "__main__":
    signal.signal(signal.SIGINT, test.cleanup)
    app.run(debug=True, host=args.ipaddress, port=args.port, use_reloader=False)
    