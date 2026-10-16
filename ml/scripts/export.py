#!/usr/bin/env python3
"""
Export model weights for backend serving.
Loads best.pt and saves a clean state_dict + config for FastAPI.
Uses fine-tuned HF model (MobileNetV3 Large).
"""
import os
import sys
import yaml
import json
import torch
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "configs" / "classes.yaml"
WEIGHTS_DIR = Path(__file__).parent.parent / "weights"
BACKEND_WEIGHTS_DIR = Path(__file__).parent.parent.parent / "backend" / "app" / "data" / "weights"

BACKEND_WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    output_classes = config["output_classes"]
    class_to_idx = {c: i for i, c in enumerate(output_classes)}
    
    checkpoint_path = WEIGHTS_DIR / "best.pt"
    if not checkpoint_path.exists():
        print(f"ERROR: No checkpoint found at {checkpoint_path}")
        print("Run train.py first")
        sys.exit(1)
    
    # Load checkpoint (our own trained model - safe)
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    
    # Extract state dict
    state_dict = checkpoint["model_state_dict"]
    
    # Save clean state dict for backend
    torch.save(state_dict, BACKEND_WEIGHTS_DIR / "model.pt")
    
    # Save class mapping and config for backend
    export_config = {
        "classes": output_classes,
        "class_to_idx": class_to_idx,
        "idx_to_class": {i: c for c, i in class_to_idx.items()},
        "subtypes": config["subtypes"],
        "confidence_threshold": config["confidence_threshold"],
        "hazardous_caution_threshold": config["hazardous_caution_threshold"],
        "image_size": config["image_size"],
        "normalize_mean": config["normalize_mean"],
        "normalize_std": config["normalize_std"],
        "model_architecture": "mobilenetv3_large",
    }
    
    with open(BACKEND_WEIGHTS_DIR / "model_config.json", "w") as f:
        json.dump(export_config, f, indent=2)
    
    print(f"Exported model to {BACKEND_WEIGHTS_DIR}")
    print(f"  model.pt (state dict)")
    print(f"  model_config.json (classes, thresholds, preprocessing)")

if __name__ == "__main__":
    main()