import os
import sys
from datetime import datetime, timedelta

def load_tide_data(filepath="tides_2026.txt"):
    tide_events = []
    if not os.path.exists(filepath):
        return tide_events
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                datetime_str, code_str = line.split()
                tide_events.append((datetime.fromisoformat(datetime_str), int(code_str)))
            except ValueError: continue
    return tide_events

def run_automation_task(code):
    """
    Put your actual layout publishing or website update logic here.
    """
    status_label = "End of outward run" if code == 1 else "End of inward run"
    print(f"TRIGGERED: Executing layout generation for: {status_label} ({code})")

def execute():
    tide_events = load_tide_data("tides_2026.txt")
    now = datetime.now()
    
    # Safety window checking 3 minutes back to handle GitHub initialization lag
    window_start = now - timedelta(minutes=3)
    
    matched = False
    for dt, code in tide_events:
        if window_start <= dt <= now:
            run_automation_task(code)
            matched = True
            break
            
    if not matched:
        print("Triggered, but no direct slack time match found in the current minute window.")

if __name__ == "__main__":
    execute()
