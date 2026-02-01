#!/usr/bin/env python3
import subprocess
import cv2
import numpy as np
import mediapipe as mp
import time
import math
import csv
from datetime import datetime
import socket

# ---------- CONFIGURACIÓN UDP ----------
ESP32_IP = "192.168.4.2"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ---------- FUNCIONES MATEMÁTICAS ----------
def angle_abc(a, b, c) -> float:
    ba = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    bc = (c[0] - b[0], c[1] - b[1], c[2] - b[2])
    dot = ba[0]*bc[0] + ba[1]*bc[1] + ba[2]*bc[2]
    nba = math.sqrt(ba[0]**2 + ba[1]**2 + ba[2]**2)
    nbc = math.sqrt(bc[0]**2 + bc[1]**2 + bc[2]**2)
    if nba == 0 or nbc == 0:
        return 180.0
    cosang = max(-1.0, min(1.0, dot / (nba * nbc)))
    return math.degrees(math.acos(cosang))

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def map_angle(ang, bent, straight) -> float:
    lo = min(bent, straight)
    hi = max(bent, straight)
    a = clamp(ang, lo, hi)
    if bent < straight:
        t = (a - bent) / (straight - bent + 1e-9)
    else:
        t = (bent - a) / (bent - straight + 1e-9)
    return 180.0 * clamp(t, 0.0, 1.0)

# ---------- ENVÍO UDP ----------
def send_angles(values):
    msg = ",".join(str(int(v)) for v in values) + "\n"
    sock.sendto(msg.encode("ascii"), (ESP32_IP, UDP_PORT))
    print("ENVIANDO:", msg.strip())

# ---------- CAPTURA DE VÍDEO ----------
def mjpeg_frames_from_rpicam(width=640, height=480, fps=30):
    cmd = [
        "rpicam-vid",
        "-t", "0",
        "--codec", "mjpeg",
        "--inline",
        "--flush",
        "--width", str(width),
        "--height", str(height),
        "--framerate", str(fps),
        "-n",
        "-o", "-"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
    buf = bytearray()
    last_t = time.time()
    try:
        while True:
            chunk = p.stdout.read(4096)
            if not chunk:
                break
            buf += chunk
            soi = buf.find(b"\xff\xd8")
            eoi = buf.find(b"\xff\xd9", soi + 2)
            if soi != -1 and eoi != -1:
                jpg = bytes(buf[soi:eoi+2])
                del buf[:eoi+2]
                img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    continue
                dt = time.time() - last_t
                last_t = time.time()
                yield img, dt
    finally:
        p.terminate()

# ---------- FUNCIONES UI ----------
def draw_bar(img, x, y, w, h, value, vmin=0, vmax=180, label=""):
    value = clamp(value, vmin, vmax)
    cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 50), -1)
    fill = int(w * (value - vmin) / (vmax - vmin + 1e-9))
    cv2.rectangle(img, (x, y), (x + fill, y + h), (0, 200, 0), -1)
    cv2.rectangle(img, (x, y), (x + w, y + h), (200, 200, 200), 1)
    cv2.putText(img, f"{label}: {int(value)}", (x, y - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1)

# ---------- PROGRAMA PRINCIPAL ----------
def main():
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    labels = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
    triplets = [(1,2,4),(5,6,7),(9,10,11),(13,14,15),(17,18,19)]
    STRAIGHT = [170,175,175,175,175]
    BENT = [70,70,70,70,70]

    NO_HAND_ANGLES = [180]*5

    smooth_angles = [None]*5
    alpha = 0.3

    log_name = f"hand_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    log_f = open(log_name, "w", newline="")
    log = csv.writer(log_f)
    log.writerow(["timestamp", *labels])

    SEND_HZ = 2
    SEND_PERIOD = 1.0 / SEND_HZ
    next_send_t = time.time()

    try:
        for frame_bgr, dt in mjpeg_frames_from_rpicam():
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                pts = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

                raw_angles = [
                    map_angle(
                        angle_abc(pts[a], pts[b], pts[c]),
                        BENT[i],
                        STRAIGHT[i]
                    )
                    for i, (a, b, c) in enumerate(triplets)
                ]

                angles = []
                for i, a in enumerate(raw_angles):
                    if smooth_angles[i] is None:
                        smooth_angles[i] = a
                    else:
                        smooth_angles[i] = alpha * a + (1 - alpha) * smooth_angles[i]
                    angles.append(smooth_angles[i])

                mp_draw.draw_landmarks(
                    frame_bgr,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style()
                )
            else:
                angles = NO_HAND_ANGLES.copy()
                smooth_angles = [180]*5

            # ---- Envío UDP ----
            if time.time() >= next_send_t:
                send_angles(angles)
                log.writerow([time.time(), *[int(a) for a in angles]])
                next_send_t = time.time() + SEND_PERIOD

            # ---- Mostrar barras ----
            base_x, base_y, bar_w, bar_h, gap = 10, 10, 200, 16, 28
            for i, angle in enumerate(angles):
                draw_bar(frame_bgr, base_x, base_y + i*gap,
                         bar_w, bar_h, angle, 0, 180, labels[i])

            cv2.imshow("Hand Tracking + Servo Angles", frame_bgr)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break

    finally:
        hands.close()
        cv2.destroyAllWindows()
        log_f.close()
        print(f"\nLog guardado en: {log_name}")

if __name__ == "__main__":
    main()


