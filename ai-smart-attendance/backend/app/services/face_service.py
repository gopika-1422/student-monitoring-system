import numpy as np
import json
import cv2
import os
import logging
from typing import List, Dict, Optional, Tuple
from scipy.spatial.distance import cosine
from app.core.config import settings

logger = logging.getLogger(__name__)

_face_app = None
_face_embeddings_cache: Dict[str, np.ndarray] = {}


def get_face_app():
    """Lazy load InsightFace model."""
    global _face_app
    if _face_app is None:
        try:
            import insightface
            from insightface.app import FaceAnalysis
            _face_app = FaceAnalysis(
                name="buffalo_sc",
                providers=["CPUExecutionProvider"],
            )
            _face_app.prepare(ctx_id=0, det_size=(640, 640))
            logger.info("InsightFace model loaded successfully")
        except Exception as e:
            logger.warning(f"InsightFace not available: {e}. Using OpenCV fallback.")
            _face_app = None
    return _face_app


def detect_faces_opencv(image: np.ndarray) -> List[Dict]:
    """Fallback face detection using OpenCV Haar Cascades."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    results = []
    for (x, y, w, h) in faces:
        face_img = image[y:y+h, x:x+w]
        results.append({
            "bbox": [x, y, x+w, y+h],
            "embedding": None,
            "confidence": 0.9,
            "face_img": face_img,
        })
    return results


def extract_faces(image: np.ndarray) -> List[Dict]:
    """Extract faces and embeddings from image."""
    app = get_face_app()
    
    if app is not None:
        try:
            faces = app.get(image)
            results = []
            for face in faces:
                results.append({
                    "bbox": face.bbox.tolist(),
                    "embedding": face.embedding.tolist() if face.embedding is not None else None,
                    "confidence": float(face.det_score),
                    "age": getattr(face, "age", None),
                    "gender": getattr(face, "gender", None),
                })
            return results
        except Exception as e:
            logger.error(f"InsightFace error: {e}")
    
    return detect_faces_opencv(image)


def compute_similarity(emb1: List[float], emb2: List[float]) -> float:
    """Compute cosine similarity between two embeddings."""
    a = np.array(emb1)
    b = np.array(emb2)
    return float(1 - cosine(a, b))


def match_face(
    query_embedding: List[float],
    known_embeddings: Dict[str, List[float]],
    threshold: float = None,
) -> Tuple[Optional[str], float]:
    """Find best matching student for a face embedding."""
    if threshold is None:
        threshold = settings.FACE_RECOGNITION_THRESHOLD
    
    best_match = None
    best_score = 0.0
    
    for student_id, stored_emb in known_embeddings.items():
        try:
            score = compute_similarity(query_embedding, stored_emb)
            if score > best_score:
                best_score = score
                best_match = student_id
        except Exception:
            continue
    
    if best_score >= threshold:
        return best_match, best_score
    return None, best_score


def load_embeddings_cache(embeddings_dir: str) -> Dict[str, List[float]]:
    """Load all student embeddings from disk."""
    cache = {}
    if not os.path.exists(embeddings_dir):
        return cache
    
    for filename in os.listdir(embeddings_dir):
        if filename.endswith(".json"):
            student_id = filename.replace(".json", "")
            filepath = os.path.join(embeddings_dir, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    cache[student_id] = data["embedding"]
            except Exception as e:
                logger.error(f"Failed to load embedding for {student_id}: {e}")
    
    return cache


def save_embedding(student_id: str, embedding: List[float], embeddings_dir: str):
    """Save student face embedding to disk."""
    os.makedirs(embeddings_dir, exist_ok=True)
    filepath = os.path.join(embeddings_dir, f"{student_id}.json")
    with open(filepath, "w") as f:
        json.dump({"student_id": student_id, "embedding": embedding}, f)


def extract_embedding_from_image_bytes(image_bytes: bytes) -> Optional[List[float]]:
    """Extract face embedding from raw image bytes."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    
    faces = extract_faces(img)
    if not faces:
        return None
    
    # Return embedding from the largest/most confident face
    best_face = max(faces, key=lambda f: f.get("confidence", 0))
    return best_face.get("embedding")


def draw_face_boxes(
    image: np.ndarray,
    detections: List[Dict],
    color=(0, 255, 100),
) -> np.ndarray:
    """Draw bounding boxes and labels on image."""
    img_copy = image.copy()
    for det in detections:
        bbox = det.get("bbox", [])
        if len(bbox) < 4:
            continue
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        label = det.get("name", "Unknown")
        confidence = det.get("confidence", 0)
        
        # Draw box
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
        
        # Draw label background
        label_text = f"{label} ({confidence:.1%})"
        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img_copy, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
        cv2.putText(img_copy, label_text, (x1 + 3, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    return img_copy
