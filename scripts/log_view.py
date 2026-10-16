#!/usr/bin/env python3
"""
ReCircle Log Viewer
Usage:
    python scripts/log_view.py              # tail build.log
    python scripts/log_view.py --errors     # show all errors
    python scripts/log_view.py --ml         # show ML training/eval
    python scripts/log_view.py --api        # show API logs
    python scripts/log_view.py --follow     # follow (tail -f)
    python scripts/log_view.py --since "1 hour ago"  # filter by time
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import re

LOG_DIR = Path(__file__).parent.parent / "logs"

def parse_time(s: str) -> datetime:
    """Parse relative time like '1 hour ago', '30 minutes ago', '2 days ago'"""
    s = s.lower().strip()
    now = datetime.now()
    
    match = re.match(r"(\d+)\s*(second|minute|hour|day|week)s?\s*ago", s)
    if match:
        val = int(match.group(1))
        unit = match.group(2)
        if unit == "second":
            return now - timedelta(seconds=val)
        elif unit == "minute":
            return now - timedelta(minutes=val)
        elif unit == "hour":
            return now - timedelta(hours=val)
        elif unit == "day":
            return now - timedelta(days=val)
        elif unit == "week":
            return now - timedelta(weeks=val)
    
    # Try absolute format
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    
    raise ValueError(f"Cannot parse time: {s}")

def filter_lines(lines, since: datetime = None, level: str = None, component: str = None):
    """Filter log lines by time, level, component"""
    pattern = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] \[(\w+)\]")
    
    for line in lines:
        match = pattern.match(line)
        if not match:
            if not since and not level and not component:
                yield line
            continue
        
        ts_str, lvl, comp = match.groups()
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        
        if since and ts < since:
            continue
        if level and lvl != level.upper():
            continue
        if component and comp != component:
            continue
        
        yield line

def main():
    parser = argparse.ArgumentParser(description="ReCircle Log Viewer")
    parser.add_argument("--file", "-f", default="build.log", help="Log file (default: build.log)")
    parser.add_argument("--errors", "-e", action="store_true", help="Show only ERROR level")
    parser.add_argument("--ml", action="store_true", help="Show ML logs (ml_train.log, ml_eval.log)")
    parser.add_argument("--api", action="store_true", help="Show API logs (api.log)")
    parser.add_argument("--frontend", action="store_true", help="Show frontend logs (frontend.log)")
    parser.add_argument("--docker", action="store_true", help="Show docker logs (docker.log)")
    parser.add_argument("--follow", "-F", action="store_true", help="Follow (tail -f)")
    parser.add_argument("--since", "-s", help="Show logs since (e.g., '1 hour ago', '30 minutes ago')")
    parser.add_argument("--level", "-l", choices=["DEBUG", "INFO", "WARN", "ERROR"], help="Filter by level")
    parser.add_argument("--component", "-c", help="Filter by component")
    parser.add_argument("--lines", "-n", type=int, default=100, help="Number of lines (default: 100)")
    args = parser.parse_args()
    
    # Determine which files to read
    files = []
    if args.ml:
        files = ["ml_train.log", "ml_eval.log"]
    elif args.api:
        files = ["api.log"]
    elif args.frontend:
        files = ["frontend.log"]
    elif args.docker:
        files = ["docker.log"]
    elif args.errors:
        files = ["errors.log"]
    else:
        files = [args.file]
    
    since_dt = parse_time(args.since) if args.since else None
    
    for fname in files:
        fpath = LOG_DIR / fname
        if not fpath.exists():
            print(f"[log_view] {fname}: not found", file=sys.stderr)
            continue
        
        print(f"\n=== {fname} ===")
        
        if args.follow:
            # Use tail -f for follow
            import subprocess
            try:
                subprocess.run(["tail", "-f", str(fpath)], check=True)
            except KeyboardInterrupt:
                pass
            except FileNotFoundError:
                print("tail command not available", file=sys.stderr)
            return
        
        # Read last N lines
        with open(fpath, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        
        # Filter
        filtered = list(filter_lines(all_lines, since_dt, args.level, args.component))
        
        # Show last N
        for line in filtered[-args.lines:]:
            print(line.rstrip())

if __name__ == "__main__":
    main()