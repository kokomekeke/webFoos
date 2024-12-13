import multiprocessing

import cv2


def put_bounding_box(image, results):
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        start = (int(x1), int(y1))
        end = (int(x2), int(y2))
        cv2.rectangle(image, start, end, color=(255, 0, 0), thickness=3)

    return image



