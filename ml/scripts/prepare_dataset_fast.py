#!/usr/bin/env python3
"""
Prepare dataset: Load HF dataset, map labels, create splits.
Optimized: directly saves to output dirs, no temp folder.
"""
import os
import sys
import yaml
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import json
from datasets import load_dataset
from PIL import Image

CONFIG_PATH = Path(__file__).parent.parent / "configs" / "classes.yaml"
HF_DATASET_NAME = "UdaraChamidu/Garbage-Classification-with-12-classes"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "prepared"
SPLIT_DIR = Path(__file__).parent.parent / "data" / "splits"
HF_CACHE_DIR = Path(__file__).parent.parent / "data" / "hf_cache"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    mappings = {m["source"]: (m["output_class"], m["subtype"]) for m in config["mappings"]}
    output_classes = config["output_classes"]
    
    # Create output directories
    for split in ["train", "val", "test"]:
        for cls in output_classes:
            (OUTPUT_DIR / split / cls).mkdir(parents=True, exist_ok=True)
    
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading HF dataset: {HF_DATASET_NAME}...")
    ds = load_dataset(HF_DATASET_NAME, cache_dir=str(HF_CACHE_DIR))
    
    if "train" in ds:
        hf_data = ds["train"]
    elif "test" in ds:
        hf_data = ds["test"]
    else:
        split_name = list(ds.keys())[0]
        hf_data = ds[split_name]
        print(f"Using split: {split_name}")
    
    print(f"Dataset size: {len(hf_data)}")
    print(f"Features: {hf_data.features}")
    
    # Collect all images with mapped labels
    all_images = []
    class_counts = {cls: 0 for cls in output_classes}
    
    for idx, item in enumerate(hf_data):
        if "label" in item:
            label_idx = item["label"]
            if hasattr(hf_data.features["label"], "names"):
                source_label = hf_data.features["label"].names[label_idx]
            else:
                source_label = str(label_idx)
        else:
            print(f"WARNING: Item {idx} has no label, skipping")
            continue
        
        source_label = source_label.lower().replace(" ", "-")
        if source_label not in mappings:
            print(f"WARNING: Unknown source label '{source_label}' - skipping")
            continue
        
        output_class, subtype = mappings[source_label]
        
        # Save image directly to output dir (train split initially)
        img = item["image"]
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        filename = f"{source_label}_{idx}.jpg"
        # We'll move to correct split later - for now save to a flat temp dir
        temp_dir = OUTPUT_DIR / "all"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / filename
        img.save(temp_path, "JPEG", quality=95)
        
        all_images.append({
            "path": temp_path,
            "output_class": output_class,
            "subtype": subtype,
            "source": source_label
        })
        class_counts[output_class] += 1
        
        if idx % 2000 == 0:
            print(f"  Processed {idx}/{len(hf_data)} images...")
    
    print(f"\nTotal images: {len(all_images)}")
    print("Class distribution:")
    for cls, count in class_counts.items():
        print(f"  {cls}: {count}")
    
    # Split: 70% train, 15% val, 15% test (stratified)
    train_val, test = train_test_split(
        all_images, test_size=0.15, stratify=[x["output_class"] for x in all_images], random_state=42
    )
    train, val = train_test_split(
        train_val, test_size=0.176, stratify=[x["output_class"] for x in train_val], random_state=42
    )
    
    print(f"\nSplit sizes: train={len(train)}, val={len(val)}, test={len(test)}")
    
    # Move files to correct split directories
    split_data = {"train": [], "val": [], "test": []}
    
    for split_name, split_images in [("train", train), ("val", val), ("test", test)]:
        for item in split_images:
            dst = OUTPUT_DIR / split_name / item["output_class"] / item["path"].name
            shutil.move(str(item["path"]), str(dst))
            split_data[split_name].append({
                "file": str(dst.relative_to(OUTPUT_DIR)),
                "class": item["output_class"],
                "subtype": item["subtype"],
                "source": item["source"]
            })
    
    # Cleanup temp dir
    shutil.rmtree(OUTPUT_DIR / "all", ignore_errors=True)
    
    # Save split metadata
    with open(SPLIT_DIR / "split_metadata.json", "w") as f:
        json.dump(split_data, f, indent=2)
    
    print(f"\nPrepared dataset at {OUTPUT_DIR}")
    print(f"Split metadata at {SPLIT_DIR}/split_metadata.json")

if __name__ == "__main__":
    main()