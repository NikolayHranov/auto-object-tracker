import numpy as np
from numpy.typing import NDArray
import pandas as pd
import cv2
import time
# import multiprocessing as mp
from .tracking_log import logger
# from .data import DEFAULT_SETTINGS, VIDEO_FORMATS


def process_img_hsv(frame, c_hsv = (0, 255, 255), c_hsv_range = (7, 15, 20)):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv)

    h = h.astype(np.int16)
    s = s.astype(np.int16)
    v = v.astype(np.int16)

    processed = (c_hsv[0] - c_hsv_range[0] < h) * (h < c_hsv[0] + c_hsv_range[0]) * (c_hsv[1] - c_hsv_range[1] < s) * (s < c_hsv[1] + c_hsv_range[1]) * (c_hsv[2] - c_hsv_range[2] < v) * (v < c_hsv[2] + c_hsv_range[2]) * 255

    return processed.astype(np.uint8)


def detect_obj(frame: NDArray[np.uint8]):
    frame = frame.astype(np.uint8)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(frame, connectivity=8)

    if num_labels <= 1:
        return None

    areas = stats[1:, cv2.CC_STAT_AREA]
    largest_idx = np.argmax(areas) + 1

    w = stats[largest_idx, cv2.CC_STAT_WIDTH]
    h = stats[largest_idx, cv2.CC_STAT_HEIGHT]

    cx, cy = centroids[largest_idx]

    return cx, cy, w, h


def center(frame, c_x, c_y, w, h, f_size_multipl=1.8):
    
    y1 = int(c_y-h*f_size_multipl//2)
    y2 = int(c_y+h*f_size_multipl//2)
    x1 = int(c_x-w*f_size_multipl//2)
    x2 = int(c_x+w*f_size_multipl//2)

    roi = frame[y1:y2, x1:x2]

    M = cv2.moments(roi)

    if M["m00"] == 0:
        return None
    
    return int(M["m10"] / M["m00"] + x1), int(M["m01"] / M["m00"] + y1)


def save_data(path, settings, tracking_data, n_fr):

    df = pd.DataFrame(tracking_data[:n_fr], columns=["n", "x0", "y0"])

    df["x"] = df["x0"] - df["x0"][1]
    df["y"] = df["y0"] - df["y0"][1]


    if "size_ration" in settings:
        size_ratio = settings["size_ratio"]

        df["x0 [m]"] = df["x0"] * size_ratio
        df["y0 [m]"] = df["y0"] * size_ratio

        df["x [m]"] = df["x"] * size_ratio
        df["y [m]"] = df["y"] * size_ratio

    if "fps" in settings:
        fps = settings["fps"]

        df["t"] = df["n"] * 1/fps
    
    df.to_csv(path + ".csv")


def track(path, settings):

    try:

        time_start = time.time()

        video = cv2.VideoCapture(path)

        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        tracking_data = np.zeros((frame_count, 3))


        ret, frame = video.read()
        
        if not ret:
            logger.error(f"Error loading first frame of {path}")
            raise FileNotFoundError(f"Video file '{path}' not found or could not be opened.")
        
        n_fr = 1

        processed_frame = process_img_hsv(frame, settings["c_hsv"], settings["c_hsv_range"])

        obj = detect_obj(processed_frame)

        if obj:
            logger.info(f"Succesfull detection of first frame of {path}: {obj}.")
        else:
            logger.error("Failed to detect object in " + path)

        x, y, w, h = obj

        fails = 0

        while n_fr <= frame_count:
            
            tracking_data[n_fr-1, :] = [n_fr, x, y]
            
            ret, frame = video.read()
            
            if not ret:
                # logger.info(f"PROCESSED {path}")
                break
                
            processed_frame = process_img_hsv(frame, settings["c_hsv"], settings["c_hsv_range"])

            center_coords = center(processed_frame, x, y, w, h)

            if center_coords:
                x, y = center_coords
                fails = 0
            else:
                # logger.warning(f"Tracking failed for frame {path}/{n_fr+1}!")
                fails += 1
            
            n_fr += 1

            if fails > settings["failed_frames_limit"]:
                logger.error(f"Tracking for {path} failed more than {settings['failed_frames_limit']} times.")
                logger.info(f"Ending tracking for {path} due an ERROR.")
                break

        video.release()

        save_data(path, settings, tracking_data, n_fr)
        
        time_end = time.time()

        logger.info(f"{path} tracked! Runtime: {time_end - time_start}.")
    
    except Exception as e:
        logger.error(f"[{path}] ERROR: {str(e)}", exc_info=True)

