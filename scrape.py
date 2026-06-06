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
    Your layout publishing/website update logic
    """
    status_label = "End of outward run" if code == 1 else "End of inward run"
    print(f"TRIGGERED: Executing layout generation for: {status_label} ({code})")

def execute():
    tide_events = load_tide_data("tides_2026.txt")
    now = datetime.now()
    
    matched = False
    print(f"Runner system clock currently reads: {now.strftime('%H:%M:%S')}")
    
    for dt, code in tide_events:
        # 1. Calculate absolute difference in total minutes between the event and the clock
        # 2. Using total_seconds() / 60 sidesteps timezone hour offsets entirely!
        minute_diff = (now - dt).total_seconds() / 60.0
        
        # We match if the event happened between 1 and 12 minutes ago.
        # This perfectly catches the '+1 minute' cron buffer PLUS up to 11 minutes of GitHub lag.
        if 1.0 <= minute_diff <= 12.0:
            print(f"Success! Found matching slack file timestamp ({dt.strftime('%H:%M')}) which was {minute_diff:.1f} minutes ago.")
            run_automation_task(code)
            matched = True
            break
            
    if not matched:
        print("Triggered, but no direct slack time match found in the current minute window.")

if __name__ == "__main__":
    execute()
