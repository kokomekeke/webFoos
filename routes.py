# import multiprocessing
# import os
#
# import cv2
# from flask import request, jsonify, send_from_directory, url_for
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# import logging
#
# from server import app
#
# UPLOAD_FOLDER = './static/'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
# logging.basicConfig(level=logging.INFO)
#
# CORS(app)
#
#
# def allowed_file(filename):
#     allowed_extensions = {'mp4', 'mov', 'avi', 'jpg', 'png'}
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in allowed_extensions
#
#
# @app.route('/videos/<filename>', methods=['GET'])
# def get_video(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#
#
# @app.route('/upload', methods=['POST'])
# def process_video():
#     try:
#         if 'file' not in request.files:
#             logging.error("No file part in the request")
#             return jsonify({"error": "No file part in the request"}), 400
#
#         file = request.files['file']
#         print(file)
#         if file.filename == '':
#             logging.error("No file selected")
#             return jsonify({"error": "No file selected"}), 400
#
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             print(filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             print(file_path)
#             file.save(file_path)
#
#             logging.info(f"File saved: {file_path}")
#
#             # Generáljuk az URL-t a fájlhoz
#             file_url = url_for('get_video', filename=filename, _external=True)
#             print("file url:", file_url)
#
#             return jsonify({
#                 "message": "File successfully uploaded",
#                 "file_url": file_url,
#             }), 200
#         else:
#             logging.error("File type not allowed")
#             return jsonify({"error": "File type not allowed"}), 400
#     except Exception as e:
#         logging.exception("Error while processing the upload")
#         return jsonify({"error": str(e)}), 500
#
#
# @app.route("/perspective", methods=["POST"])
# def perspective():
#     try:
#         data = request.get_json()  # JSON adatok beolvasása a kérésből
#         print(data)
#         if not data or "coordinates" not in data:
#             return jsonify({"error": "Missing 'coordinates' field"}), 400
#
#         # Debug: Kiíratjuk a beérkező adatokat
#         print(f"Received coordinates: {data['coordinates']}")
#
#         print("asdd")
#         # border_rect(data['coordinates'])
#         video = cv2.VideoCapture("./static/foos11.mp4")
#         frame_queue = multiprocessing.Queue()
#
#
#         print("asdd")
#
#         # Példa válasz
#         return jsonify({"message": "Coordinates received successfully!"}), 200
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({"error": "An error occurred"}), 500