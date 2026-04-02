"""
Face Recognition Model - Standalone utility
Usage: python face_model.py --image path/to/image.jpg --students-dir path/to/embeddings
"""
import argparse
import json
import os
import sys
import numpy as np

try:
    import cv2
    from insightface.app import FaceAnalysis
    from scipy.spatial.distance import cosine
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("InsightFace not installed. Using OpenCV fallback.")
    import cv2


def load_model():
    if not INSIGHTFACE_AVAILABLE:
        return None
    app = FaceAnalysis(name="buffalo_sc", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app


def extract_embedding(image_path: str, model) -> dict:
    """Extract face embedding from an image file."""
    img = cv2.imread(image_path)
    if img is None:
        return {"error": f"Cannot read image: {image_path}"}

    if model is None:
        # OpenCV fallback
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(gray, 1.1, 5)
        return {
            "faces_detected": len(faces),
            "embedding": None,
            "note": "InsightFace not available - install for real embeddings",
        }

    faces = model.get(img)
    if not faces:
        return {"faces_detected": 0, "embedding": None}

    best = max(faces, key=lambda f: f.det_score)
    return {
        "faces_detected": len(faces),
        "embedding": best.embedding.tolist(),
        "confidence": float(best.det_score),
        "bbox": best.bbox.tolist(),
    }


def register_student(image_path: str, student_id: str, embeddings_dir: str, model):
    """Register a student's face embedding."""
    result = extract_embedding(image_path, model)
    if result.get("error"):
        print(f"Error: {result['error']}")
        return False
    if not result.get("embedding"):
        print(f"No face detected in {image_path}")
        return False

    os.makedirs(embeddings_dir, exist_ok=True)
    out_path = os.path.join(embeddings_dir, f"{student_id}.json")
    with open(out_path, "w") as f:
        json.dump({"student_id": student_id, "embedding": result["embedding"]}, f)
    print(f"✅ Registered {student_id} -> {out_path} (confidence: {result['confidence']:.3f})")
    return True


def match_student(image_path: str, embeddings_dir: str, model, threshold: float = 0.6):
    """Match a face against all registered students."""
    result = extract_embedding(image_path, model)
    if not result.get("embedding"):
        print("No face detected in query image")
        return None

    query_emb = np.array(result["embedding"])
    best_match = None
    best_score = 0.0

    for fname in os.listdir(embeddings_dir):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(embeddings_dir, fname)) as f:
            data = json.load(f)
        score = float(1 - cosine(query_emb, np.array(data["embedding"])))
        if score > best_score:
            best_score = score
            best_match = data["student_id"]

    if best_score >= threshold:
        print(f"✅ Match: {best_match} (score: {best_score:.3f})")
        return best_match, best_score
    else:
        print(f"❌ No match (best: {best_match}, score: {best_score:.3f})")
        return None, best_score


def main():
    parser = argparse.ArgumentParser(description="Face Recognition Utility")
    parser.add_argument("--mode", choices=["extract", "register", "match"], default="extract")
    parser.add_argument("--image", required=True)
    parser.add_argument("--student-id", default="STU001")
    parser.add_argument("--embeddings-dir", default="./storage/embeddings")
    parser.add_argument("--threshold", type=float, default=0.6)
    args = parser.parse_args()

    model = load_model()

    if args.mode == "extract":
        result = extract_embedding(args.image, model)
        print(json.dumps(result, indent=2))
    elif args.mode == "register":
        register_student(args.image, args.student_id, args.embeddings_dir, model)
    elif args.mode == "match":
        match_student(args.image, args.embeddings_dir, model, args.threshold)


if __name__ == "__main__":
    main()
