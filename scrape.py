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
    Your actual layout publishing or website update logic goes here.
    """
    status_label = "End of outward run" if code == 1 else "End of inward run"
    print(f"TRIGGERED: Executing layout generation for: {status_label} ({code})")

def execute():
    tide_events = load_tide_data("tides_2026.txt")
    
    # 1. Get the current raw UTC time from the GitHub Runner clock
    github_utc_now = datetime.utcnow() 
    
    # 2. Convert it to Atlantic Daylight Time (ADT is UTC - 3 hours)
    # This aligns the runner perfectly with the timezone in tides_2026.txt
    now_atlantic = github_utc_now - timedelta(hours=3)
    
    print(f"GitHub Runner clock (UTC):   {github_utc_now.strftime('%Y-%m-%d %I:%M:%S %p')}")
    print(f"Converted to Atlantic Time:  {now_atlantic.strftime('%Y-%m-%d %I:%M:%S %p')}")
    
    matched = False
    for dt, code in tide_events:
        # Calculate exactly how many minutes ago the slack tide happened 
        # relative to our newly corrected Atlantic clock
        minute_diff = (now_atlantic - dt).total_seconds() / 60.0
        
        # Match if the event occurred between 1 and 15 minutes ago 
        # (This easily absorbs any heavy GitHub startup delays)
        if 1.0 <= minute_diff <= 15.0:
            print(f"Success! Found matching slack file timestamp ({dt.strftime('%I:%M %p')}) which was {minute_diff:.1f} minutes ago.")
            run_automation_task(code)
            matched = True
            break
            
    if not matched:
        print("No direct slack time match found in the current minute window.")

if __name__ == "__main__":
    execute()
