import os
import sys
from datetime import datetime, timezone, timedelta

def load_tide_data(filepath="tides_2026.txt"):
    tide_events = []
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
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

def run_automation_task(event_1, event_2):
    """
    Your actual layout generation/website update logic goes here.
    It now receives BOTH upcoming events as tuples: (datetime, code)
    """
    dt1, code1 = event_1
    dt2, code2 = event_2
    
    label1 = "End of outward run" if code1 == 1 else "End of inward run"
    label2 = "End of outward run" if code2 == 1 else "End of inward run"
    
    print("\n--- PULLING NEXT TWO SLACK TIDES ---")
    print(f"1st Upcoming: {dt1.strftime('%Y-%m-%d %I:%M %p')} -> {label1} ({code1})")
    print(f"2nd Upcoming: {dt2.strftime('%Y-%m-%d %I:%M %p')} -> {label2} ({code2})")
    print("------------------------------------\n")
    
    # 1. Format your strings for the HTML layout display
    slack_time_1 = dt1.strftime('%I:%M %p')
    slack_time_2 = dt2.strftime('%I:%M %p')
    slack_date_1 = dt1.strftime('%B %d, %Y')
    
    # 2. Re-insert your original HTML template here.
    # (Use f-strings to inject slack_time_1, label1, etc. into your dashboard layout)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Martinon Yacht Club - Tide Dashboard</title>
</head>
<body>
    <h1>Upcoming Slack Tides</h1>
    <p>Data updated on: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>
    
    <div class="tide-box">
        <h3>Next Slack</h3>
        <p>Time: {slack_time_1}</p>
        <p>Type: {label1}</p>
    </div>
    
    <div class="tide-box">
        <h3>Following Slack</h3>
        <p>Time: {slack_time_2}</p>
        <p>Type: {label2}</p>
    </div>
</body>
</html>
"""

    # 3. THIS IS THE CRITICAL STEP: Write the fresh HTML code directly to the runner file system
    with open("index.html", "w") as f:
        f.write(html_content)
        
    print("Successfully rewrote index.html with new upcoming slack tide metrics.")
    
def execute():
    tide_events = load_tide_data("tides_2026.txt")
    
    # Get the current time and align it to Atlantic Time (UTC - 3)
    from datetime import timezone
    github_utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    now_atlantic = github_utc_now - timedelta(hours=3)
    
    print(f"Current Local Atlantic Time: {now_atlantic.strftime('%Y-%m-%d %I:%M:%S %p')}")
    
    upcoming_events = []
    
    # Scan the file for events that are in the future relative to right now
    for dt, code in tide_events:
        if dt > now_atlantic:
            upcoming_events.append((dt, code))
        
        # Stop scanning once we have grabbed the next two
        if len(upcoming_events) == 2:
            break
            
    if len(upcoming_events) == 2:
        run_automation_task(upcoming_events[0], upcoming_events[1])
    else:
        print(f"Could not find two upcoming events. Found: {len(upcoming_events)}")

if __name__ == "__main__":
    execute()
