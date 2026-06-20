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
    Generates index.html with the original clean layout and wording.
    """
    dt1, code1 = event_1
    dt2, code2 = event_2
    
    # Get current date in Atlantic time to compare for "Tonight" vs "Tomorrow"
    from datetime import datetime, timezone, timedelta
    github_utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    now_atlantic = github_utc_now - timedelta(hours=3)
    today_date = now_atlantic.date()
    tomorrow_date = today_date + timedelta(days=1)
    
    # Helper to format the time prefix (Today/Tonight/Tomorrow/Date)
    def get_day_label(dt):
        if dt.date() == today_date:
            # If it's past 5 PM, "Tonight" feels more natural than "Today"
            return "Tonight" if dt.hour >= 18 else "Today"
        elif dt.date() == tomorrow_date:
            return "Tomorrow"
        else:
            return dt.strftime('%A') # Fallback to day name (e.g., Sunday)

    # 1. Reconstruct the original labels
    label1 = "End of outward run" if code1 == 0 else "End of inward run"
    label2 = "End of outward run" if code2 == 0 else "End of inward run"
    
    # 2. Build the precise display strings
    line1 = f"{get_day_label(dt1)} at {dt1.strftime('%-I:%M %p')} — {label1}"
    line2 = f"{get_day_label(dt2)} at {dt2.strftime('%-I:%M %p')} — {label2}"
    
    print("\n--- REWRITING INDEX.HTML WITH ORIGINAL FORMAT ---")
    print(line1)
    print(line2)
    print("-------------------------------------------------\n")
    
    # 3. Write out the clean HTML template matching your dashboard's style
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Upcoming Slack Water</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            padding: 5px;
            background-color: #ffffff;
            color: #333333;
            text-align: center;
        }}
        h1 {{
            font-size: 1.5rem;
            color: #111111;
            margin-bottom: 5px;
        }}
        p {{
            font-size: 1.1rem;
            margin: 4px 0;
        }}
    </style>
</head>
<body>

    <h1>Upcoming Slack Water at Reversing Falls</h1>
    <p>{line1}</p>
    <p>{line2}</p>

</body>
</html>
"""

    with open("index.html", "w") as f:
        f.write(html_content)
        
    print("Successfully restored index.html to the original 3 PM layout style.")
    
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
