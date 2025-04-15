import cv2
import json
import threading
import time
import numpy as np
from flask import Flask
from flask_socketio import SocketIO, emit
from deepface import DeepFace
from ultralytics import YOLO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load YOLO model
try:
    yolo_model = YOLO("yolov8n.pt")
    print("✅ YOLOv8 Model Loaded Successfully")
except Exception as e:
    print(f"❌ YOLO Model Load Error: {e}")

emotion_counts = {}
detected_objects = set()
lock = threading.Lock()


def detect_emotion(frame):
    """Detects the dominant emotion in a frame using DeepFace."""
    global emotion_counts
    try:
        # Convert frame to RGB (DeepFace expects RGB format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Analyze emotions
        emotion_result = DeepFace.analyze(
            rgb_frame, actions=["emotion"], detector_backend="opencv", enforce_detection=False
        )

        if isinstance(emotion_result, list) and emotion_result:
            emotion = emotion_result[0].get("dominant_emotion", "neutral")
            with lock:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            print(f"🟢 Detected Emotion: {emotion}")  # Debugging

    except Exception as e:
        print(f"❌ Emotion Detection Error: {e}")


def detect_objects(frame):
    """Detects objects in the given frame using YOLOv8."""
    global detected_objects
    try:
        results = yolo_model(frame, conf=0.25, iou=0.4)

        with lock:
            if results[0].boxes.data.shape[0] > 0:
                detected_objects.update([results[0].names[int(obj[5])] for obj in results[0].boxes.data])

        print(f"🟢 Detected Objects: {detected_objects}")  # Debugging

    except Exception as e:
        print(f"❌ Object Detection Error: {e}")


@socketio.on("start_detection")
def process_frames():
    global emotion_counts, detected_objects
    emotion_counts = {}
    detected_objects.clear()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        emit("detection_result", {"error": "❌ Webcam not accessible"})
        print("❌ Webcam not accessible")
        return

    start_time = time.time()

    while time.time() - start_time < 10:  # Run for 10 seconds
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            continue

        # Run detection in separate threads
        emotion_thread = threading.Thread(target=detect_emotion, args=(frame,))
        object_thread = threading.Thread(target=detect_objects, args=(frame,))
        emotion_thread.start()
        object_thread.start()

        # Wait for threads to finish before starting new ones
        emotion_thread.join()
        object_thread.join()

    cap.release()

    # Determine dominant emotion
    dominant_emotion = max(emotion_counts, key=emotion_counts.get, default="neutral")

    # Save results
    data = {"emotion": dominant_emotion, "context": list(detected_objects)}
    with open("static/emotion_context.json", "w") as f:
        json.dump(data, f)

    emit("detection_result", data)
    print(f"✅ Detection Complete: {data}")


if __name__ == "__main__":
    socketio.run(app, debug=True)
