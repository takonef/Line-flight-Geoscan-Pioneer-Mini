import math
import cv2
import numpy as np

NEAR_BY_PIXELS = 61
EDGE = 15


def flight_follow_line(frame, frame_center_x):
    target_circle_x, frame_after_thresh, dx_center, dangle = get_black_line(frame)
    dV_max = 150  # коэффициент для полета вправо/влево
    dVx = dV_max * (dx_center / frame_center_x)

    dVrot_k = 230  # коэффициент для рысканья

    limit = 100
    if dVx > limit:
        dVx = limit
    if dVx < -limit:
        dVx = -limit

    ch_2 = 1500 - int(dVrot_k * dangle)
    ch_4 = 1500 + int(dVx)
    ch_3 = 1425  # вперед

    return frame_after_thresh, 5 if target_circle_x == 0 else 3, ch_2, ch_3, ch_4


def calculate_start_and_target(bw_frame, width, height):
    def calculate_median(sum_columns):
        sum_left = 0
        sum_right = 0
        i_left = 0
        i_right = width - 1

        while i_left != i_right:
            if sum_left < sum_right:
                sum_left += 255 * height // 2 - sum_columns[i_left]
                i_left += 1
            else:
                sum_right += 255 * height // 2 - sum_columns[i_right]
                i_right -= 1

        return i_left

    # верхняя часть массива
    sum_columns_top = np.sum(bw_frame[0: height // 2], axis=0)
    target_circle_x = calculate_median(sum_columns_top)
    target_circle_y = height // 4

    # средняя часть массива
    sum_columns_center = np.sum(bw_frame[height // 4: 3 * height // 4], axis=0)
    start_circle_x = calculate_median(sum_columns_center)
    start_circle_y = height // 2

    return start_circle_x, start_circle_y, target_circle_x, target_circle_y


def get_black_line(frame):
    height = frame.shape[0]
    width = frame.shape[1]

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blurred_frame = cv2.GaussianBlur(gray_frame, (19, 19), 0)
    bw_frame = cv2.adaptiveThreshold(blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                     NEAR_BY_PIXELS, EDGE)

    start_circle_x, start_circle_y, target_circle_x, target_circle_y = calculate_start_and_target(bw_frame, width,
                                                                                                  height)

    bw_frame = cv2.cvtColor(bw_frame, cv2.COLOR_GRAY2BGR)

    arrow_color = (0, 0, 255) # green
    bw_frame = cv2.arrowedLine(bw_frame, (start_circle_x, start_circle_y), (target_circle_x, target_circle_y),
                               arrow_color, 2)

    return target_circle_x, bw_frame, target_circle_x - width // 2, math.atan2(target_circle_x - start_circle_x,
                                                                               height // 4)


def change_near_by_pixels(sign, value=10):
    global NEAR_BY_PIXELS
    NEAR_BY_PIXELS += sign * value


def change_edge(sign, value=2):
    global EDGE
    EDGE += sign * value
