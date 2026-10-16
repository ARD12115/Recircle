#!/usr/bin/env python3
"""
Simple script: move temp images to prepared split directories.
"""
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import json
import yaml

CONFIG_PATH = Path(__file__).parent.parent / "configs" / "classes.yaml"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "prepared"
SPLIT_DIR = Path(__file__).parent.parent / "data" / "splits"
TEMP_DIR = Path(__file__).parent.parent / "data" / "temp_hf_images"

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
    
    # Get all temp files
    temp_files = list(TEMP_DIR.glob("*.jpg"))
    print(f"Found {len(temp_files)} temp images")
    
    # Parse class from filename
    all_items = []
    for f in temp_files:
        source_label = f.stem.split("_")[0]  # battery_0.jpg -> battery
        if source_label not in {m["source"] for m in config["mappings"]}:
            # Try matching without the index part
            parts = f.stem.split("_")
            if len(parts) > 1:
                source_label = "_".join(parts[:-1])
        if source_label in mappings:
            output_class, subtype = mappings[source_label]
            all_items.append({"path": f, "output_class": output_class, "subtype": subtype, "source": source_label})
        else:
            print(f"Unknown: {f.name}")
    
    print(f"Mapped {len(all_items)} images")
    
    # Count per class
    class_counts = {cls: 0 for cls in output_classes}
    for item in all_items:
        class_counts[item["output_class"]] += 1
    for cls, count in class_counts.items():
        print(f"  {cls}: {count}")
    
    # Split: 70% train, 15% val, 15% test
    train_val, test = train_test_split(
        all_items, test_size=0.15, stratify=[x["output_class"] for x in all_items], random_state=42
    )
    train, val = train_test_split(
        train_val, test_size=0.176, stratify=[x["output_class"] for x in train_val], random_state=42
    )
    
    print(f"\nSplit sizes: train={len(train)}, val={len(val)}, test={len(test)}")
    
    # Move files
    split_data = {"train": [], "val": [], "test": []}
    
    for split_name, split_items in [("train", train), ("val", val), ("test", test)]:
        for item in split_items:
            dst = OUTPUT_DIR / split_name / item["output_class"] / item["path"].name
            shutil.move(str(item["path"]), str(dst))
            split_data[split_name].append({
                "file": str(dst.relative_to(OUTPUT_DIR)),
                "class": item["output_class"],
                "subtype": item["subtype"],
                "source": item["source"]
            })
    
    # Save split metadata
    with open(SPLIT_DIR / "split_metadata.json", "w") as f:
        json.dump(split_data, f, indent=2)
    
    print(f"\nDone! Dataset at {OUTPUT_DIR}")

if __name__ == "__main__":
    main()