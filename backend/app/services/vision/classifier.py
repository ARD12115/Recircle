"""
Vision Classifier - Model load and predict
Uses fine-tuned HF model (MobileNetV3 Large).
"""
import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from pathlib import Path
from typing import List, Tuple
import numpy as np

from app.core.config import settings

# Global model instance
_model = None
_model_config = None
_class_to_idx = None
_idx_to_class = None
_device = None


def get_device():
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def load_model():
    """Load model at startup. Called from main.py lifespan."""
    global _model, _model_config, _class_to_idx, _idx_to_class
    
    model_path = Path(settings.MODEL_PATH)
    config_path = Path(settings.MODEL_CONFIG_PATH)
    
    if not model_path.exists():
        print(f"WARNING: Model not found at {model_path}. Classification will fail.")
        return False
    
    if not config_path.exists():
        print(f"WARNING: Model config not found at {config_path}")
        return False
    
    with open(config_path) as f:
        _model_config = json.load(f)
    
    _class_to_idx = _model_config["class_to_idx"]
    _idx_to_class = _model_config["idx_to_class"]
    
    num_classes = len(_model_config["classes"])
    
    # Create model architecture (MobileNetV3 Large to match fine-tuned HF model)
    _model = models.mobilenet_v3_large(weights=None)
    in_features = _model.classifier[-1].in_features
    _model.classifier[-1] = nn.Linear(in_features, num_classes)
    
    # Load weights
    state_dict = torch.load(model_path, map_location=get_device(), weights_only=True)
    _model.load_state_dict(state_dict)
    _model.to(get_device())
    _model.eval()
    
    print(f"Model loaded: {num_classes} classes on {get_device()} (arch: {_model_config.get('model_architecture', 'mobilenetv3_large')})")
    return True


def preprocess_image(image: Image.Image) -> torch.Tensor:
    """Preprocess PIL image for model input."""
    if _model_config is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    transform = transforms.Compose([
        transforms.Resize((_model_config["image_size"], _model_config["image_size"])),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=_model_config["normalize_mean"],
            std=_model_config["normalize_std"]
        ),
    ])
    
    return transform(image).unsqueeze(0).to(get_device())


def predict(image: Image.Image) -> Tuple[str, str, float, List[Tuple[str, float]]]:
    """
    Run inference on image.
    Returns: (predicted_class, subtype, confidence, top3_list)
    """
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    input_tensor = preprocess_image(image)
    
    with torch.no_grad():
        outputs = _model(input_tensor)
        probs = torch.softmax(outputs, dim=1)
        conf, pred_idx = torch.max(probs, 1)
        
        predicted_class = _idx_to_class[pred_idx.item()]
        confidence = conf.item()
        
        # Top-3
        top3_probs, top3_idx = torch.topk(probs, 3, dim=1)
        top3 = [
            (_idx_to_class[i.item()], top3_probs[0, j].item())
            for j, i in enumerate(top3_idx[0])
        ]
    
    # Get subtype
    subtype = _model_config["subtypes"].get(predicted_class, ["unknown"])[0]
    
    return predicted_class, subtype, confidence, top3


def get_model_info() -> dict:
    """Get model info for health check."""
    if _model is None:
        return {"loaded": False}
    return {
        "loaded": True,
        "classes": _model_config["classes"],
        "device": str(get_device()),
        "confidence_threshold": _model_config["confidence_threshold"],
        "architecture": _model_config.get("model_architecture", "mobilenetv3_large"),
    }