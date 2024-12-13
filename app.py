import multiprocessing
import os
from queue import Queue
import time

import cv2
import toml
from flask import request, jsonify, send_from_directory, url_for, Flask, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
from server.videoProcessor import VideoProcessor

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})


UPLOAD_FOLDER = 'static/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)

foos_file = None
rect_points = []
prog_queue = Queue(100)

with open('configuration.toml', 'r') as f:
    config = toml.load(f)


def allowed_file(filename):
    allowed_extensions = {'mp4', 'mov', 'avi', 'jpg', 'png'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def serve_vue_app():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def catch_all(path):
    # Ellenőrizzük, hogy létezik-e a fájl
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Ha nem létezik, akkor az index.html-t adjuk vissza
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/videos/<filename>', methods=['GET'])
def get_video(filename):
    print("asdd", app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype='video/mp4')


@app.route('/upload', methods=['POST'])
def process_video():
    try:
        if 'file' not in request.files:
            logging.error("No file part in the request")
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        print(file)
        if file.filename == '':
            logging.error("No file selected")
            return jsonify({"error": "No file selected"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(file_path)
            global foos_file
            foos_file = file_path
            file.save(file_path)

            logging.info(f"File saved: {file_path}")

            # Generáljuk az URL-t a fájlhoz
            file_url = url_for('get_video', filename=filename, _external=True)
            print("file url:", file_url)

            return jsonify({
                "message": "File successfully uploaded",
                "file_url": file_url,
            }), 200
        else:
            logging.error("File type not allowed")
            return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        logging.exception("Error while processing the upload")
        return jsonify({"error": str(e)}), 500


@app.route("/perspective", methods=["POST"])
def perspective():
    try:
        data = request.get_json()  # JSON adatok beolvasása a kérésből
        if not data or "coordinates" not in data:
            return jsonify({"error": "Missing 'coordinates' field"}), 400

        # Debug: Kiíratjuk a beérkező adatokat
        print(f"Received coordinates: {data['coordinates']}")

        global rect_points
        rect_points = data['coordinates']
        print(len(rect_points))

        vp = VideoProcessor(foos_file, rect_points, prog_queue, config)


        # Példa válasz
        return jsonify({"message": "Coordinates received successfully!"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route("/stream", methods=["GET"])
def stream():
    def generate():
        while True:
            try:
                # Próbáljunk meg egy elemet kiolvasni a `prog_queue`-ból, ha van.
                progress = prog_queue.get(timeout=1)  # Timeout 1 másodperc
                yield f"data: {progress}\n\n"

                # Ha a feldolgozás véget ért (100% vagy queue üres), kilépünk.
                if progress >= 100:
                    break
            except Exception as e:
                # Ha nincs több adat a queue-ban, várjunk kicsit.
                time.sleep(0.1)

    return Response(generate(), content_type="text/event-stream")


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    app.run(debug=True, threaded=False)
