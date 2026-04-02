"""
Emotion Detection Model - Standalone utility
Uses DeepFace for emotion analysis and OpenCV for head pose estimation.
Usage: python emotion_model.py --image path/to/image.jpg
"""
import argparse
import json
import cv2
import numpy as np
import sys

EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
EMOTION_COLORS = {
    "happy":    (0, 200, 100),
    "neutral":  (150, 150, 150),
    "sad":      (200, 100, 0),
    "angry":    (0, 0, 200),
    "surprise": (0, 165, 255),
    "fear":     (128, 0, 128),
    "disgust":  (0, 150, 0),
}


def detect_emotion(image: np.ndarray) -> dict:
    """Detect emotion from face image using DeepFace."""
    try:
        from deepface import DeepFace
        result = DeepFace.analyze(image, actions=["emotion"], enforce_detection=False, silent=True)
        if isinstance(result, list):
            result = result[0]
        dominant = result.get("dominant_emotion", "neutral")
        emotions = result.get("emotion", {})
        return {
            "dominant": dominant,
            "confidence": emotions.get(dominant, 50) / 100,
            "all": {k: round(v / 100, 3) for k, v in emotions.items()},
        }
    except ImportError:
        print("DeepFace not installed. Install: pip install deepface")
        return {"dominant": "neutral", "confidence": 0.5, "all": {}}
    except Exception as e:
        return {"dominant": "neutral", "confidence": 0.5, "error": str(e)}


def estimate_attention(face_region: np.ndarray) -> dict:
    """Estimate attention level based on eye openness and head orientation."""
    if face_region is None or face_region.size == 0:
        return {"is_attentive": True, "eye_ratio": 1.0}

    try:
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        eyes = eye_cascade.detectMultiScale(gray, 1.1, 3, minSize=(15, 15))
        eye_count = len(eyes)
        is_attentive = eye_count >= 1
        return {
            "is_attentive": is_attentive,
            "eyes_detected": eye_count,
            "note": "Open eyes detected" if is_attentive else "No eyes detected (possibly closed or looking away)",
        }
    except Exception as e:
        return {"is_attentive": True, "error": str(e)}


def analyze_image(image_path: str, show: bool = False) -> dict:
    """Full emotion + attention analysis on a static image."""
    img = cv2.imread(image_path)
    if img is None:
        return {"error": f"Cannot read: {image_path}"}

    # Face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

    results = []
    for (x, y, w, h) in faces:
        face_roi = img[y:y+h, x:x+w]
        emotion_data = detect_emotion(face_roi)
        attention_data = estimate_attention(face_roi)

        face_result = {
            "bbox": [int(x), int(y), int(x+w), int(y+h)],
            "emotion": emotion_data,
            "attention": attention_data,
        }
        results.append(face_result)

        if show:
            color = EMOTION_COLORS.get(emotion_data["dominant"], (200, 200, 200))
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            label = f"{emotion_data['dominant']} ({emotion_data['confidence']:.0%})"
            cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            status = "👀 Attentive" if attention_data["is_attentive"] else "😴 Distracted"
            cv2.putText(img, status, (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    if show and len(faces) > 0:
        cv2.imshow("Emotion Analysis", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return {"image": image_path, "faces_found": len(faces), "results": results}


def realtime_emotion():
    """Run real-time emotion detection from webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    print("Press 'q' to quit")
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        # Process every 5th frame for performance
        if frame_count % 5 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

            for (x, y, w, h) in faces:
                face_roi = frame[y:y+h, x:x+w]
                emotion_data = detect_emotion(face_roi)
                color = EMOTION_COLORS.get(emotion_data["dominant"], (200, 200, 200))

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                label = f"{emotion_data['dominant']} {emotion_data['confidence']:.0%}"
                cv2.putText(frame, label, (x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.putText(frame, f"Frame: {frame_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Real-time Emotion Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Emotion Detection Utility")
    parser.add_argument("--mode", choices=["image", "realtime"], default="image")
    parser.add_argument("--image", help="Path to image file")
    parser.add_argument("--show", action="store_true", help="Display annotated image")
    args = parser.parse_args()

    if args.mode == "realtime":
        realtime_emotion()
    else:
        if not args.image:
            parser.error("--image required for image mode")
        result = analyze_image(args.image, args.show)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
