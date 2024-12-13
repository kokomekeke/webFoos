import os
import time
from threading import Thread, Event

import cv2
import numpy as np
from torch import Tensor
from ultralytics import YOLO

from server.Predictor import Predictor
from server.utils import calculate_dist, find_line_coordinate

model = YOLO("./detect/train/weights/best.pt")


class VideoProcessor:
    def __init__(self, video, perspective_points, prog_q, config):
        self.video = cv2.VideoCapture(video)
        self.perspectivePoints = perspective_points
        self.finishedProcessing = False
        self.playAllowed = False
        self.prog_q = prog_q
        self.outputWidth = 0
        self.outputHeight = 0
        self.predictor = Predictor(config['video_processer']['predictor_size'])
        self.config = config
        # ezt majd visszarakni, csak ameddig tesztelem a kiegyenesített képpel, addig kikomment
        # self.output = cv2.VideoWriter(
        #     'processed.mp4',
        #     cv2.VideoWriter_fourcc(*'MP4V'),
        #     video.get(cv2.CAP_PROP_FPS),
        #     (
        #         int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
        #         int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #     )
        # )
        self.output = None
        self.stop_event = Event()
        self.imgProcessor = Thread(target=self.processor)
        self.imgProcessor.start()
        self.ia = True

    def put_bounding_box(self, frame, results):
        if self.predictor.has_prediction:
            last_point = self.predictor.fifo.getLast()[0]
            last_point = int(last_point[0]), int(last_point[1])
            future_position = self.predictor.predict()
            print("lp:", last_point)
            print("pp:", future_position)
            if self.predictor.get_speed() == 0:
                cv2.line(frame, last_point, future_position, (255, 0, 0), 3)
            else:
                if self.predictor.get_speed() < 3000000000:
                    p3x, p3y = find_line_coordinate(last_point[0], last_point[1], future_position[0], future_position[1], 60)
                    p3x, p3y = int(p3x), int(p3y)
                    cv2.line(frame, last_point, (p3x, p3y), (255, 0, 0), 2)
                elif self.predictor.get_speed() < 6000000000:
                    p3x, p3y = find_line_coordinate(last_point[0], last_point[1], future_position[0], future_position[1], 100)
                    p3x, p3y = int(p3x), int(p3y)
                    cv2.line(frame, last_point, (p3x, p3y), (0, 255, 0), 2)
                else:
                    p3x, p3y = find_line_coordinate(last_point[0], last_point[1], future_position[0], future_position[1],
                                                    150)
                    p3x, p3y = int(p3x), int(p3y)
                    cv2.line(frame, last_point, (p3x, p3y), (0, 0, 255), 2)

        for box in results[0].boxes:
            cls = box.cls
            if isinstance(cls, Tensor):
                cls = int(cls.item())
            else:
                cls = int(cls)

            if cls == 0:
                curr_time = time.time()
                box_points = box.xyxy[0].tolist()
                box_center = ((box_points[0] + box_points[2]) / 2, (box_points[1] + box_points[3]) / 2)
                box_center = (box_center, curr_time)
                self.predictor.add(box_center)

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            start = (int(x1), int(y1))
            end = (int(x2), int(y2))

            cv2.rectangle(frame, start, end, color=(255, 0, 0), thickness=1)

        return frame

    def process_frame(self, frame, conf):
        res = model.predict(frame, conf=conf)
        return self.put_bounding_box(frame, res)

    def processor(self):
        length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        i = 0
        while not self.stop_event.is_set():
            if i > length / 2:
                self.playAllowed = True
            ret, frame = self.video.read()
            if not ret:
                self.prog_q.put(int((i / length) * 100))
                self.stop_event.set()
                self.stop()
                break

            processed_frame = self.analyze_frame(frame)

            self.outputHeight, self.outputWidth, *_ = processed_frame.shape
            parent_directory = os.path.dirname(os.path.abspath(__file__))
            # Az új szülő szülője könyvtár meghatározása
            # grandparent_directory = os.path.dirname(parent_directory)

            # Fájl elérési út
            # file_path = os.path.join(parent_directory, 'processed.mp4')
            output_path = os.path.join(os.getcwd(), 'static', 'processed.mp4')
            print("opath", output_path)
            if i == 0:
                self.output = cv2.VideoWriter(
                    output_path,
                    cv2.VideoWriter_fourcc(*'MP4V'),
                    self.video.get(cv2.CAP_PROP_FPS),
                    (
                        int(self.outputWidth),
                        int(self.outputHeight)
                    )
                )
            self.output.write(processed_frame)

            self.prog_q.put(int((i / length) * 100))
            i += 1

        if self.output:
            self.output.release()
            self.video.release()
            print("Video file has been saved.")

        print("finished processing")
        self.finishedProcessing = True

    def analyze_frame(self, frame):
        # ret, frame = self.video.read()
        # pts1 = np.float32(self.perspectivePoints)
        # pts1 = np.array([pts1[0], pts1[3], pts1[1], pts1[2]], dtype=np.float32)
        pts1 = np.array([[point['x'], point['y']] for point in self.perspectivePoints], dtype=np.float32)

        # Átrendezés, hogy megfeleljen az OpenCV elvárásainak
        pts1 = np.array([pts1[0], pts1[3], pts1[1], pts1[2]], dtype=np.float32)

        # Szélesség és magasság számítása
        width_top = calculate_dist(pts1[0], pts1[1])  # Bal felső -> Jobb felső
        width_bottom = calculate_dist(pts1[2], pts1[3])  # Bal alsó -> Jobb alsó
        height_left = calculate_dist(pts1[0], pts1[2])  # Bal felső -> Bal alsó
        height_right = calculate_dist(pts1[1], pts1[3])  # Jobb felső -> Jobb alsó

        width = max(int(width_top), int(width_bottom))
        height = max(int(height_left), int(height_right))

        # Perspektív transzformáció célpont pontjai
        pts2 = np.float32([
            [0, 0],  # Bal felső
            [width, 0],  # Jobb felső
            [0, height],  # Bal alsó
            [width, height]  # Jobb alsó
        ])

        # Perspektív transzformáció mátrixa
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        # Transzformált kép
        result = cv2.warpPerspective(frame, matrix, (width, height))

        # Kép további feldolgozása
        return self.process_frame(result, self.config['video_processer']['model_confidence'])

    def stop(self):
        self.stop_event.set()
        self.imgProcessor.join()
        if self.output:
            self.output.release()
        self.video.release()
        print("Processor stopped.")
