import sys
import os
from datetime import datetime
import pytz

def main():
    # Target file name in your repo
    data_file = "tides_2026.txt"
    
    if not os.path.exists(data_file):
        print(f"⚠️ Local database file {data_file} missing from repository context.")
        sys.exit(0)

    # Setup local New Brunswick time context
    tz = pytz.timezone('America/Halifax')
    # Match your original format tracking setup
    now = datetime.now(tz).replace(tzinfo=None)

    upcoming_events = []

    print(f"📥 Loading local database footprint... Current local time: {now}")
    
    with open(data_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        try:
            # Parse the format: YYYY-MM-DDTHH:MM:SS DIRECTION_CODE
            date_str, dir_str = line.split()
            event_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            
            # Check if this prediction is ahead of our current clock boundary
            if event_time > now:
                if "0" in dir_str:
                    run_text = "End of inward run"
                elif "1" in dir_str:
                    run_text = "End of outward run"
                else:
                    run_text = "Slack Water"
                    
                upcoming_events.append({
                    "time": event_time,
                    "run_text": run_text
                })
                
                # Stop processing once we collect the next two matching slacks
                if len(upcoming_events) == 2:
                    break
        except Exception as e:
            continue

    if upcoming_events:
        # Build the dynamic HTML element blocks
        list_items_html = ""
        for event in upcoming_events:
            date_display = event["time"].strftime('%B %d')
            time_display = event["time"].strftime('%-I:%M %p') # Cleans leading zero out on Linux
            run_display = event["run_text"]
            
            list_items_html += f"        <div class='event-row'><strong>{date_display}</strong> at {time_display} — <em>{run_display}</em></div>\n"

        # Construct your preferred layout template
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Next Tide Events - Reversing Falls</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding-top: 5vh; background-color: white; color: #333; }}
        .container {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; text-align: left; }}
        h1 {{ margin-top: 0; font-size: 1.4rem; color: #444; border-bottom: 2px solid #eeec; padding-bottom: 10px; margin-bottom: 15px; }}
        .event-row {{ font-size: 1.25rem; color: #0056b3; margin: 12px 0; line-height: 1.4; }}
        .event-row strong {{ color: #111; }}
        .event-row em {{ color: #555; font-style: normal; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Upcoming Slack Water at Reversing Falls</h1>
{list_items_html}    </div>
</body>
</html>"""

        with open("index.html", "w") as f:
            f.write(html_content)
        print(f"🎉 Success! Locally verified index.html updated with {len(upcoming_events)} events.")
    else:
        print("⚠️ Database processed completely, but no upcoming events found in data window.")

if __name__ == "__main__":
    main()
