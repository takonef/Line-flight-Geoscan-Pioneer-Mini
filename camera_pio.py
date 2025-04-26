import cv2
import numpy as np
import socket

ip = '192.168.4.1'
port = 8888
video_buffer_size = 65000
timeout = 0.5
tcp = None
udp = None
raw_video_frame = bytes()
connected = False


def new_tcp():
    """Returns new TCP socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    return sock


def new_udp():
    """Returns new UDP socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    return sock


def connect():
    global tcp, udp, connected
    """Connect to TCP and UDP sockets. Creates new ones if necessary."""
    disconnect()
    tcp = new_tcp()
    udp = new_udp()
    try:
        tcp.connect((ip, port))
        udp.bind(tcp.getsockname())
    except TimeoutError:
        return False
    return True


def disconnect():
    """Disconnect."""
    global tcp, udp, connected
    connected = False
    if tcp is not None:
        tcp.close()
        tcp = None
    if udp is not None:
        udp.close()
        udp = None


def get_frame():
    global connected, video_buffer_size
    global raw_video_frame
    try:
        if not connected:
            if connect():
                connected = True
                print('Camera CONNECTED')
            else:
                return None
        _video_frame_buffer, addr = udp.recvfrom(video_buffer_size)
        beginning = _video_frame_buffer.find(b'\xff\xd8')
        if beginning == -1:
            return None
        _video_frame_buffer = _video_frame_buffer[beginning:]
        end = _video_frame_buffer.find(b'\xff\xd9')
        if end == -1:
            return None
        raw_video_frame = _video_frame_buffer[:end + 2]
        return raw_video_frame
    except TimeoutError:
        if connected:
            connected = False
            print('Camera DISCONNECTED')
        return None


def get_cv_frame():
    """
    get cv_frame
    :return: cv_frame or None
    """

    frame = get_frame()
    if frame is not None:
        frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
    return frame
