#!/usr/bin/env python3
"""
Evaluate trained model: confusion matrix, per-class recall, own-photo realism test.
Uses fine-tuned HF model (AmadFR/ecovision_mobilenetv3 -> MobileNetV3 Large).
"""
import os
import sys
import yaml
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from torchvision.models import MobileNet_V3_Large_Weights
from PIL import Image
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

CONFIG_PATH = Path(__file__).parent.parent / "configs" / "classes.yaml"
DATA_DIR = Path(__file__).parent.parent / "data" / "prepared"
WEIGHTS_DIR = Path(__file__).parent.parent / "weights"
REPORTS_DIR = Path(__file__).parent.parent / "reports"
OWN_PHOTOS_DIR = Path(__file__).parent.parent / "own_photos"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class GarbageDataset(Dataset):
    def __init__(self, split, transform=None):
        self.split = split
        self.transform = transform
        self.samples = []
        
        split_dir = DATA_DIR / split
        for class_dir in split_dir.iterdir():
            if not class_dir.is_dir():
                continue
            class_name = class_dir.name
            for img_path in class_dir.glob("*.jpg"):
                self.samples.append((img_path, class_name))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, class_name = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, class_name


class OwnPhotosDataset(Dataset):
    def __init__(self, transform=None):
        self.transform = transform
        self.samples = []
        
        if OWN_PHOTOS_DIR.exists():
            for img_path in OWN_PHOTOS_DIR.glob("*.jpg"):
                self.samples.append(img_path)
            for img_path in OWN_PHOTOS_DIR.glob("*.png"):
                self.samples.append(img_path)
            for img_path in OWN_PHOTOS_DIR.glob("*.jpeg"):
                self.samples.append(img_path)
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, img_path.name


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def get_model(num_classes):
    """Create MobileNetV3 Large with custom head (matches fine-tuned HF model)."""
    model = models.mobilenet_v3_large(weights=None)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    return model


def evaluate():
    config = load_config()
    output_classes = config["output_classes"]
    num_classes = len(output_classes)
    class_to_idx = {c: i for i, c in enumerate(output_classes)}
    idx_to_class = {i: c for c, i in class_to_idx.items()}
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Transform
    val_transform = transforms.Compose([
        transforms.Resize((config["image_size"], config["image_size"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=config["normalize_mean"], std=config["normalize_std"]),
    ])
    
    # Test dataset
    test_dataset = GarbageDataset("test", val_transform)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=4)
    
    print(f"Test samples: {len(test_dataset)}")
    
    # Load model
    model = get_model(num_classes).to(device)
    checkpoint = torch.load(WEIGHTS_DIR / "best.pt", map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    print(f"Loaded model from epoch {checkpoint['epoch']}, val_acc={checkpoint['val_acc']:.4f}")
    
    # Evaluate on test set
    test_preds, test_targets = [], []
    test_probs = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Test Evaluation"):
            images = images.to(device)
            targets = torch.tensor([class_to_idx[l] for l in labels]).to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            test_preds.extend(preds.cpu().numpy())
            test_targets.extend(targets.cpu().numpy())
            test_probs.extend(probs.cpu().numpy())
    
    test_acc = accuracy_score(test_targets, test_preds)
    print(f"\nTest Accuracy: {test_acc:.4f}")
    
    # Per-class metrics
    report = classification_report(test_targets, test_preds, target_names=output_classes, output_dict=True)
    print("\nPer-class metrics:")
    for cls in output_classes:
        r = report[cls]
        print(f"  {cls}: precision={r['precision']:.3f}, recall={r['recall']:.3f}, f1={r['f1-score']:.3f}, support={r['support']}")
    
    # Hazardous recall check
    hazardous_recall = report["hazardous"]["recall"]
    print(f"\nHazardous recall: {hazardous_recall:.3f} (target: ≥0.90)")
    if hazardous_recall < 0.90:
        print("  ⚠️  BELOW TARGET - consider increasing class weight or lowering threshold")
    
    # Confusion matrix
    cm = confusion_matrix(test_targets, test_preds)
    
    # Save confusion matrix image
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=output_classes, yticklabels=output_classes)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix (Test Set - Fine-tuned HF Model)")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    
    # Evaluate own photos (realism check)
    print("\n--- Realism Check (Own Photos) ---")
    own_results = []
    if OWN_PHOTOS_DIR.exists():
        own_dataset = OwnPhotosDataset(val_transform)
        own_loader = DataLoader(own_dataset, batch_size=1, shuffle=False)
        
        with torch.no_grad():
            for images, filenames in tqdm(own_loader, desc="Own Photos"):
                images = images.to(device)
                outputs = model(images)
                probs = torch.softmax(outputs, dim=1)
                conf, pred = torch.max(probs, 1)
                
                pred_class = idx_to_class[pred.item()]
                confidence = conf.item()
                top3_idx = torch.topk(probs, 3, dim=1).indices[0].tolist()
                top3 = [(idx_to_class[i], probs[0, i].item()) for i in top3_idx]
                
                own_results.append({
                    "file": filenames[0],
                    "predicted_class": pred_class,
                    "confidence": confidence,
                    "top3": top3
                })
                
                print(f"  {filenames[0]}: {pred_class} ({confidence:.3f}) - top3: {[(c, f'{p:.3f}') for c, p in top3]}")
    else:
        print(f"  No own photos found at {OWN_PHOTOS_DIR}")
        print("  Add photos to ml/own_photos/ for realism check")
    
    # Save comprehensive report
    with open(REPORTS_DIR / "metrics.json", "w") as f:
        json.dump({
            "test_accuracy": test_acc,
            "val_accuracy": checkpoint["val_acc"],
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "classes": output_classes,
            "hazardous_recall": hazardous_recall,
            "own_photos_results": own_results,
            "config": config
        }, f, indent=2)
    
    print(f"\nReports saved to {REPORTS_DIR}")

if __name__ == "__main__":
    evaluate()