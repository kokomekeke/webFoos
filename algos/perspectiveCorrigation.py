
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("./detect/train/weights/best.pt")

video = cv2.VideoCapture("./static/foos11.mp4")
rval, frame = video.read()
print(frame.shape)


def region_contours(img, x_1, y_1, x_2, y_2):
    region = img[y_1:y_2, x_1:x_2]
    gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_region, 100, 255, cv2.THRESH_BINARY)
    gray_region_colored = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    print("contours ", contours)
    # draw contours on the original image
    image_copy = region.copy()
    cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2,
                                   lineType=cv2.LINE_AA)

    frame[y_1:y_2, x_1:x_2] = image_copy
    return frame


def border_rect(data):

    cv2.line(frame, (data[0]['x'], data[0]['y']), (data[1]['x'], data[1]['y']), (0, 255, 0), 3)
    cv2.line(frame, (data[1]['x'], data[1]['y']), (data[2]['x'], data[2]['y']), (0, 255, 0), 3)
    cv2.line(frame, (data[2]['x'], data[2]['y']), (data[3]['x'], data[3]['y']), (0, 255, 0), 3)
    cv2.line(frame, (data[3]['x'], data[3]['y']), (data[0]['x'], data[0]['y']), (0, 255, 0), 3)

    cv2.imshow("frame", frame)

    pts1 = np.float32([
        [data[0]['x'], data[0]['y']],
        [data[1]['x'], data[1]['y']],
        [data[3]['x'], data[3]['y']],
        [data[2]['x'], data[2]['y']]
    ])

    height1 = np.sqrt(((data[0]['y'] - data[1]['y']) ** 2) + ((data[0]['x'] - data[1]['x']) ** 2))
    height2 = np.sqrt(((data[3]['y'] - data[2]['y']) ** 2) + ((data[3]['x'] - data[2]['x']) ** 2))

    width1 = np.sqrt(((data[0]['y'] - data[2]['y']) ** 2) + ((data[0]['x'] - data[2]['x']) ** 2))
    width2 = np.sqrt(((data[1]['y'] - data[3]['y']) ** 2) + ((data[1]['x'] - data[3]['x']) ** 2))

    max_height = max(int(height1), int(height2))
    max_width = max(int(width1), int(width2))

    print(max_height, max_width)

    pts2 = np.float32([
        [0, 0],  # Bal felső
        [0, max_height],  # Bal alsó
        [max_width, 0],  # Jobb felső
        [max_width, max_height]  # Jobb alsó
    ])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result1 = cv2.warpPerspective(frame, matrix, (max_width, max_height), flags=cv2.INTER_AREA)
    cv2.imshow("res", result1)
    results = model.predict(result1, conf=0.5)
    print(results)

    for result in results:
        for box in result.boxes:
            print("b:", box.xyxy[0].tolist())
            x1, y1, x2, y2 = box.xyxy[0].tolist()  # Convert tensor to a list
            # Ensure coordinates are integers
            start = (int(x1), int(y1))
            end = (int(x2), int(y2))
            # Draw a filled rectangle on the image
            cv2.rectangle(result1, start, end, color=(255, 0, 0), thickness=-1)
            # result1 = region_contours(result, start[0], start[1], end[0], end[1])

    cv2.imshow("res", result1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

