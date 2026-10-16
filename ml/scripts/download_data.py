#!/usr/bin/env python3
"""
Verify HF dataset access for UdaraChamidu/Garbage-Classification-with-12-classes.
No download needed - prepare_dataset.py loads it directly via datasets library.
"""
import sys
from datasets import load_dataset

HF_DATASET_NAME = "UdaraChamidu/Garbage-Classification-with-12-classes"

def main():
    print(f"Verifying access to HF dataset: {HF_DATASET_NAME}...")
    
    try:
        ds = load_dataset(HF_DATASET_NAME)
        print(f"✅ Dataset accessible")
        print(f"   Splits: {list(ds.keys())}")
        for split_name, split_data in ds.items():
            print(f"   {split_name}: {len(split_data)} samples")
            if hasattr(split_data.features.get("label"), "names"):
                print(f"   Classes: {split_data.features['label'].names}")
        return True
    except Exception as e:
        print(f"❌ Failed to access dataset: {e}")
        print("   Check internet connection and HF token if private")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)