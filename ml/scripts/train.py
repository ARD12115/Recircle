#!/usr/bin/env python3
"""
Train classifier: fine-tune pretrained HF model (AmadFR/ecovision_mobilenetv3) 
on mapped 5-class dataset. Only trains the classifier head.
"""
import os
import sys
import yaml
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from torchvision.models import MobileNet_V3_Large_Weights
from PIL import Image
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
from tqdm import tqdm
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file as load_safetensors

CONFIG_PATH = Path(__file__).parent.parent / "configs" / "classes.yaml"
DATA_DIR = Path(__file__).parent.parent / "data" / "prepared"
WEIGHTS_DIR = Path(__file__).parent.parent / "weights"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
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


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_hf_backbone(config):
    """
    Load pretrained MobileNetV3 Large from HF (AmadFR/ecovision_mobilenetv3),
    strip its 10-class classifier, attach new 5-class head.
    Freeze backbone, only train head.
    """
    num_classes = len(config["output_classes"])
    hf_repo = config["hf_model_repo"]
    hf_file = config["hf_model_file"]
    
    # Create MobileNetV3 Large architecture (matches HF model)
    model = models.mobilenet_v3_large(weights=None)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    
    # Load HF weights
    print(f"Loading pretrained weights from {hf_repo}/{hf_file}...")
    try:
        if hf_file.endswith(".safetensors"):
            local_path = hf_hub_download(repo_id=hf_repo, filename=hf_file)
            state_dict = load_safetensors(local_path)
        else:
            local_path = hf_hub_download(repo_id=hf_repo, filename=hf_file)
            state_dict = torch.load(local_path, map_location="cpu", weights_only=True)
    except Exception as e:
        print(f"  Failed to load {hf_file}: {e}")
        print("  Trying ImageNet weights as fallback...")
        model = models.mobilenet_v3_large(weights=MobileNet_V3_Large_Weights.IMAGENET1K_V1)
        model.classifier[-1] = nn.Linear(in_features, num_classes)
        return model
    
    # Strip HF classifier keys (they're for 10 classes)
    backbone_state = {k: v for k, v in state_dict.items() 
                      if not k.startswith("classifier.3.") and not k.startswith("classifier.4.")}
    
    # Load backbone weights (strict=False ignores new head)
    missing, unexpected = model.load_state_dict(backbone_state, strict=False)
    print(f"  Loaded backbone: {len([k for k in state_dict if not k.startswith('classifier')])} params")
    print(f"  Missing (new head): {missing}")
    
    # Freeze backbone
    for name, param in model.named_parameters():
        if "classifier" not in name:
            param.requires_grad = False
    
    # Verify only head is trainable
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  Trainable params: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")
    
    return model


def train():
    config = load_config()
    output_classes = config["output_classes"]
    class_weights = torch.tensor([config["class_weights"][c] for c in output_classes], dtype=torch.float32)
    num_classes = len(output_classes)
    class_to_idx = {c: i for i, c in enumerate(output_classes)}
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Transforms (same as HF model training)
    train_transform = transforms.Compose([
        transforms.Resize((config["image_size"], config["image_size"])),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.RandomResizedCrop(config["image_size"], scale=(0.8, 1.0)),
        transforms.ToTensor(),
        transforms.Normalize(mean=config["normalize_mean"], std=config["normalize_std"]),
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((config["image_size"], config["image_size"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=config["normalize_mean"], std=config["normalize_std"]),
    ])
    
    # Datasets
    train_dataset = GarbageDataset("train", train_transform)
    val_dataset = GarbageDataset("val", val_transform)
    test_dataset = GarbageDataset("test", val_transform)
    
    print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
    
    train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True, num_workers=config["num_workers"])
    val_loader = DataLoader(val_dataset, batch_size=config["batch_size"], shuffle=False, num_workers=config["num_workers"])
    test_loader = DataLoader(test_dataset, batch_size=config["batch_size"], shuffle=False, num_workers=config["num_workers"])
    
    # Model: Load HF pretrained, freeze backbone, attach 5-class head
    model = load_hf_backbone(config).to(device)
    
    # Loss and optimizer (only head params)
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
    head_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.AdamW(head_params, lr=config["learning_rate"], weight_decay=config["weight_decay"])
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config["epochs"])
    
    best_val_acc = 0.0
    
    for epoch in range(config["epochs"]):
        # Training
        model.train()
        train_loss = 0.0
        train_preds, train_targets = [], []
        
        for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{config['epochs']} [Train]"):
            images = images.to(device)
            targets = torch.tensor([class_to_idx[l] for l in labels]).to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            train_preds.extend(preds.cpu().numpy())
            train_targets.extend(targets.cpu().numpy())
        
        train_acc = accuracy_score(train_targets, train_preds)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_preds, val_targets = [], []
        
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc=f"Epoch {epoch+1}/{config['epochs']} [Val]"):
                images = images.to(device)
                targets = torch.tensor([class_to_idx[l] for l in labels]).to(device)
                
                outputs = model(images)
                loss = criterion(outputs, targets)
                
                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_preds.extend(preds.cpu().numpy())
                val_targets.extend(targets.cpu().numpy())
        
        val_acc = accuracy_score(val_targets, val_preds)
        scheduler.step()
        
        print(f"Epoch {epoch+1}: Train Loss={train_loss/len(train_loader):.4f}, Train Acc={train_acc:.4f}, Val Loss={val_loss/len(val_loader):.4f}, Val Acc={val_acc:.4f}")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "epoch": epoch,
                "val_acc": val_acc,
                "class_to_idx": class_to_idx,
                "config": config
            }, WEIGHTS_DIR / "best.pt")
            print(f"  Saved best model (val_acc={val_acc:.4f})")
    
    # Final evaluation on test set
    print("\nEvaluating on test set...")
    model.eval()
    test_preds, test_targets = [], []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Test"):
            images = images.to(device)
            targets = torch.tensor([class_to_idx[l] for l in labels]).to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            test_preds.extend(preds.cpu().numpy())
            test_targets.extend(targets.cpu().numpy())
    
    test_acc = accuracy_score(test_targets, test_preds)
    print(f"\nTest Accuracy: {test_acc:.4f}")
    
    # Classification report
    report = classification_report(test_targets, test_preds, target_names=output_classes, output_dict=True)
    print(classification_report(test_targets, test_preds, target_names=output_classes))
    
    # Confusion matrix
    cm = confusion_matrix(test_targets, test_preds)
    
    # Save reports
    with open(REPORTS_DIR / "metrics.json", "w") as f:
        json.dump({
            "test_accuracy": test_acc,
            "best_val_accuracy": best_val_acc,
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "classes": output_classes
        }, f, indent=2)
    
    # Save confusion matrix as image
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=output_classes, yticklabels=output_classes)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix (Fine-tuned HF Model)")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    
    print(f"\nReports saved to {REPORTS_DIR}")
    print(f"Best model saved to {WEIGHTS_DIR}/best.pt")


if __name__ == "__main__":
    train()