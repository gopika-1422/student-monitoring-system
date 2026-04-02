import numpy as np
import cv2
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

_emotion_model = None
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


def get_emotion_model():
    global _emotion_model
    if _emotion_model is None:
        try:
            from deepface import DeepFace
            _emotion_model = DeepFace
            logger.info("DeepFace emotion model loaded")
        except Exception as e:
            logger.warning(f"DeepFace not available: {e}")
            _emotion_model = None
    return _emotion_model


def detect_emotion_deepface(face_img: np.ndarray) -> Dict:
    """Detect emotion using DeepFace."""
    model = get_emotion_model()
    if model is None:
        return {"emotion": "neutral", "confidence": 0.5, "all_emotions": {}}
    
    try:
        result = model.analyze(
            face_img,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )
        if isinstance(result, list):
            result = result[0]
        
        dominant = result.get("dominant_emotion", "neutral")
        emotions = result.get("emotion", {})
        confidence = emotions.get(dominant, 50) / 100.0
        
        return {
            "emotion": dominant,
            "confidence": confidence,
            "all_emotions": {k: v / 100.0 for k, v in emotions.items()},
        }
    except Exception as e:
        logger.error(f"Emotion detection error: {e}")
        return {"emotion": "neutral", "confidence": 0.5, "all_emotions": {}}


def estimate_head_pose(landmarks: Optional[np.ndarray], image_shape: Tuple) -> Dict:
    """Estimate head pose from facial landmarks."""
    if landmarks is None:
        return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_attentive": True}
    
    h, w = image_shape[:2]
    
    # 3D model points (generic face model)
    model_points = np.array([
        (0.0, 0.0, 0.0),          # Nose tip
        (0.0, -330.0, -65.0),     # Chin
        (-225.0, 170.0, -135.0),  # Left eye corner
        (225.0, 170.0, -135.0),   # Right eye corner
        (-150.0, -150.0, -125.0), # Left mouth
        (150.0, -150.0, -125.0),  # Right mouth
    ], dtype=np.float64)
    
    # Camera matrix
    focal_length = w
    center = (w / 2, h / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1],
    ], dtype=np.float64)
    
    dist_coeffs = np.zeros((4, 1))
    
    try:
        # Use 5 key landmarks if available
        if len(landmarks) >= 5:
            image_points = np.array([
                landmarks[2],  # Nose
                landmarks[0],  # Left eye
                landmarks[1],  # Right eye
                landmarks[3],  # Left mouth
                landmarks[4],  # Right mouth
            ][:6], dtype=np.float64)
            
            if len(image_points) < 4:
                return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_attentive": True}
            
            success, rotation_vec, translation_vec = cv2.solvePnP(
                model_points[:len(image_points)],
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )
            
            if success:
                rotation_mat, _ = cv2.Rodrigues(rotation_vec)
                pose_mat = cv2.hconcat([rotation_mat, translation_vec])
                _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
                
                pitch = float(euler_angles[0])
                yaw = float(euler_angles[1])
                roll = float(euler_angles[2])
                
                # Attention: roughly looking forward
                is_attentive = abs(yaw) < 30 and abs(pitch) < 20
                
                return {
                    "yaw": yaw,
                    "pitch": pitch,
                    "roll": roll,
                    "is_attentive": is_attentive,
                }
    except Exception as e:
        logger.error(f"Head pose estimation error: {e}")
    
    return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_attentive": True}


def analyze_activity(prev_frame: Optional[np.ndarray], curr_frame: np.ndarray) -> Dict:
    """Detect movement / activity level between frames."""
    if prev_frame is None:
        return {"is_active": True, "motion_score": 0.0}
    
    try:
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        diff = cv2.absdiff(prev_gray, curr_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        motion_score = float(np.sum(thresh)) / thresh.size
        
        return {
            "is_active": motion_score > 0.001,
            "motion_score": motion_score,
        }
    except Exception as e:
        logger.error(f"Activity detection error: {e}")
        return {"is_active": True, "motion_score": 0.0}
