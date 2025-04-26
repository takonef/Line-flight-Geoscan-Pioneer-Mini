import cv2

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)


def recognize_marker_get_center(frame, marker_id):
    global detector
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(frame_gray)

    if ids is None:
        return None, None

    cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    if len(ids) != 1 or ids[0] != marker_id:
        return None, None

    marker_x_center = (corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]) // 4
    marker_y_center = (corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]) // 4

    return marker_x_center, marker_y_center


def is_marker_in_center_area_by_id(frame, marker_id, frame_center_x, frame_center_y):
    marker_x_center, marker_y_center = recognize_marker_get_center(frame, marker_id)
    return is_marker_in_center_area(frame, marker_x_center, marker_y_center, frame_center_x, frame_center_y)


def is_marker_in_center_area(frame, marker_xc, marker_yc, frame_center_x, frame_center_y):
    window_for_marker = 50  # окно для маркера в пикселях

    res = False
    rect_color = (0, 0, 0) # black

    if marker_xc is not None:
        if (abs(marker_xc - frame_center_x) <= window_for_marker and
                abs(marker_yc - frame_center_y) <= window_for_marker):
            res = True
            rect_color = (0, 255, 0)  #green
        else:
            rect_color = (0, 0, 255) #red

    cv2.rectangle(frame, (frame_center_x - window_for_marker, frame_center_y - window_for_marker),
                  (frame_center_x + window_for_marker, frame_center_y + window_for_marker), rect_color, 2)
    return res



def stabilize_at_marker(frame, marker_id, frame_center_x, frame_center_y):
    frame, dVx_aruco, dVy_aruco, dx, dy, marker_xc, marker_yc = aruco_detected(frame, marker_id, frame_center_x, frame_center_y)
    ch_3 = ch_4 = 1500
    if dVx_aruco is not None and dVy_aruco is not None:
        color_for_arrow = (255, 0, 0) # blue
        frame = cv2.arrowedLine(frame, (frame_center_x, frame_center_y),
                                (frame_center_x + dx, frame_center_y + dy), color_for_arrow, 2)
        ch_3 += int(dVy_aruco)
        ch_4 += int(dVx_aruco)

    return frame, ch_3, ch_4, marker_xc, marker_yc


def aruco_detected(frame, marker_id, xc, yc):
    global detector
    marker_xc, marker_yc = recognize_marker_get_center(frame, marker_id)
    dVy_aruco = None
    dVx_aruco = None
    dx, dy = 0, 0
    if marker_xc is not None:
        dx = int(-(xc - marker_xc))
        dy = int(-(yc - marker_yc))

        dV_aruco = 150  # коэффициент для центрирования вправо/влево
        dVx_aruco = dV_aruco * (dx / xc)
        dVy_aruco = dV_aruco * (dy / xc)

        limit = 100

        if dVx_aruco > limit:
            dVx_aruco = limit
        if dVx_aruco < -limit:
            dVx_aruco = -limit

        if dVy_aruco > limit:
            dVy_aruco = limit
        if dVy_aruco < -limit:
            dVy_aruco = -limit
    return frame, dVx_aruco, dVy_aruco, dx, dy, marker_xc, marker_yc
