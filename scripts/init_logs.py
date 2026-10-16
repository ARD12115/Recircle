#!/usr/bin/env python3
"""
ReCircle Log System Initialization
Run once to set up logging infrastructure.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"

def init_logs():
    """Initialize log directory and create placeholder files."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    log_files = [
        "build.log",
        "ml_train.log",
        "ml_eval.log",
        "api.log",
        "frontend.log",
        "docker.log",
        "errors.log",
    ]
    
    for fname in log_files:
        fpath = LOGS_DIR / fname
        if not fpath.exists():
            fpath.write_text(f"# {fname} - ReCircle log file\n# Created: {__import__('datetime').datetime.now().isoformat()}\n\n", encoding="utf-8")
            print(f"Created: {fpath}")
        else:
            print(f"Exists: {fpath}")
    
    print(f"\nLog directory: {LOGS_DIR}")
    print("Run 'make logs-log' to follow build.log")
    print("Run 'make logs-errors' to see all errors")
    print("Run 'make logs-ml' to see ML training/eval logs")

if __name__ == "__main__":
    init_logs()