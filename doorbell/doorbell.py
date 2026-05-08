import cv2
import numpy as np
import time
import os
import threading
import csv
import requests
from datetime import datetime
from deepface import DeepFace

# ── Configuration ──
KNOWN_FACES_DIR   = "../known_faces"
VISITOR_LOGS_DIR  = "../visitor_logs"
UNKNOWN_SNAPS_DIR = "../unknown_snapshots"
LOG_FILE          = os.path.join(VISITOR_LOGS_DIR, "visitor_log.csv")

# ── Telegram Configuration ──
TELEGRAM_TOKEN   = "8698646774:AAFFB_tDlm9sohzrt_1CRYy5Uq9Xcu98HR0"
TELEGRAM_CHAT_ID = "7850395773"

# ── Create directories ──
os.makedirs(VISITOR_LOGS_DIR, exist_ok=True)
os.makedirs(UNKNOWN_SNAPS_DIR, exist_ok=True)

# ── Create CSV ──
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Date", "Time", "Status"])

# ── Face detector ──
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# ── Shared variables ──
current_name  = ""
current_box   = None
lock          = threading.Lock()
is_processing = False
last_logged   = {}

# ── Send Telegram Text Message ──
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        })
        print(f"  Telegram message sent!")
    except Exception as e:
        print(f"  Telegram message error: {e}")

# ── Send Telegram Photo ──
def send_telegram_photo(image_path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(image_path, "rb") as photo:
            requests.post(url, data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption
            }, files={"photo": photo})
        print(f"  Telegram photo sent!")
    except Exception as e:
        print(f"  Telegram photo error: {e}")

# ── Log visitor to CSV ──
def log_visitor(name, status):
    now      = datetime.now()
    date     = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, date, time_str, status])
    print(f"  Logged: {name} | {date} | {time_str} | {status}")

# ── Save unknown snapshot ──
def save_snapshot(frame, x, y, w, h):
    x = max(0, x)
    y = max(0, y)
    snapshot = frame[y:y+h, x:x+w]
    if snapshot.size == 0:
        return None
    filename = os.path.join(
        UNKNOWN_SNAPS_DIR,
        f"unknown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )
    cv2.imwrite(filename, snapshot)
    print(f"  Snapshot saved: {filename}")
    return filename

# ── Face Recognition Thread ──
def recognize_face(frame):
    global current_name, current_box, is_processing

    try:
        # Step 1 — Detect faces with Haar
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))

        if len(faces) == 0:
            with lock:
                current_name = ""
                current_box  = None
            is_processing = False
            return

        # Step 2 — DeepFace recognition
        try:
            results = DeepFace.find(
                img_path=frame,
                db_path=KNOWN_FACES_DIR,
                model_name="Facenet",
                detector_backend="opencv",
                enforce_detection=False,
                silent=True
            )

            if results and not results[0].empty:
                best      = results[0].iloc[0]
                distance  = float(best["distance"])
                threshold = float(best["threshold"])

                if distance < threshold:
                    # ✅ Known face
                    identity = best["identity"]
                    name     = os.path.splitext(os.path.basename(identity))[0].capitalize()
                    x = int(best["source_x"])
                    y = int(best["source_y"])
                    w = int(best["source_w"])
                    h = int(best["source_h"])

                    with lock:
                        current_name = name
                        current_box  = (x, y, w, h)

                    # Log + Telegram message for known
                    now = time.time()
                    if name not in last_logged or now - last_logged[name] > 30:
                        last_logged[name] = now
                        log_visitor(name, "Known")
                        send_telegram_message(
                            f"✅ Welcome {name}!\n"
                            f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}\n"
                            f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}"
                        )
                else:
                    # ❌ Unknown
                    raise Exception("Unknown face")

            else:
                raise Exception("No match found")

        except:
            # ❌ Unknown face detected
            x, y, w, h = [int(faces[0][i]) for i in range(4)]
            with lock:
                current_name = "Unknown"
                current_box  = (x, y, w, h)

            now = time.time()
            if "unknown" not in last_logged or now - last_logged["unknown"] > 30:
                last_logged["unknown"] = now
                log_visitor("Unknown", "Unknown")

                # Save snapshot
                snapshot_path = save_snapshot(frame, x, y, w, h)

                # Send Telegram alert with photo
                if snapshot_path:
                    threading.Thread(
                        target=send_telegram_photo,
                        args=(snapshot_path,
                              f"🚨 Unknown Visitor!\n"
                              f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}\n"
                              f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}"),
                        daemon=True
                    ).start()

    except Exception as e:
        print(f"Error: {e}")
        with lock:
            current_name = ""
            current_box  = None

    is_processing = False

# ── Start Webcam ──
cap         = cv2.VideoCapture(0)
prev_time   = 0
frame_count = 0

print("🔔 Smart Doorbell Started!")
print(f"   Logging to  : {LOG_FILE}")
print(f"   Snapshots   : {UNKNOWN_SNAPS_DIR}")
print(f"   Telegram    : Connected ✅")
print("   Press Q to quit\n")

# Send startup message
send_telegram_message("🔔 Smart Doorbell is now Online!")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_count += 1

    # Run recognition every 10 frames
    if frame_count % 10 == 0 and not is_processing:
        is_processing = True
        thread = threading.Thread(
            target=recognize_face,
            args=(frame.copy(),),
            daemon=True
        )
        thread.start()

    # Draw results
    with lock:
        name = current_name
        box  = current_box

    if box and name != "":
        x, y, w, h = box
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.rectangle(frame, (x, y+h-35), (x+w, y+h), color, -1)
        cv2.putText(frame, name, (x+6, y+h-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # HUD
    curr_time = time.time()
    fps       = int(1 / (curr_time - prev_time + 0.001))
    prev_time = curr_time
    time_now  = datetime.now().strftime("%H:%M:%S")
    date_now  = datetime.now().strftime("%Y-%m-%d")

    cv2.putText(frame, f"FPS: {fps}",    (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"{date_now}",     (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"{time_now}",     (10, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, "Smart Doorbell",  (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,(255, 255, 0), 2)

    cv2.imshow("Smart Doorbell System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Send shutdown message
send_telegram_message("🔴 Smart Doorbell is now Offline!")
print("\nDoorbell stopped!")