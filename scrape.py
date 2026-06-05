import sys
from datetime import datetime
import requests
import pytz

# Official Government API endpoint for Saint John / Reversing Falls (Station 00066)
# This API handles server-to-server requests without blocking GitHub Actions
URL = "https://api-tides.gc.ca/v1/stations/00066/data?heights-or-currents=currents&time-zone=UTC"

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API Connection issue: {e}")
        sys.exit(0)

    # Setup the local New Brunswick time context
    tz = pytz.timezone('America/Halifax')
    now = datetime.now(tz)

    upcoming_events = []

    # Loop through the JSON array returned by the API
    for item in data:
        # The API provides standard ISO strings like "2026-06-05T17:51:00Z"
        event_str = item.get("eventDate")
        event_type = item.get("type", "")
        
        if not event_str:
            continue
            
        try:
            # Parse the timestamp as UTC, then convert it to local Atlantic Time
            utc_time = datetime.strptime(event_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            event_time = utc_time.astimezone(tz)
            
            # Check if this event happens in the future
            if event_time > now:
                # The API explicitly flags slack water turning points
                if "Slack" in event_type or item.get("velocity") == 0.0:
                    
                    # Look at the text notes or code to match your inward/outward logic
                    # Turn to Flood = Water turning to run inward
                    # Turn to Ebb = Water turning to run outward
                    type_lower = event_type.lower()
                    if "flood" in type_lower:
                        run_text = "End of outward run"
                    elif "ebb" in type_lower:
                        run_text = "End of inward run"
                    else:
                        run_text = "Slack Water"
                        
                    upcoming_events.append({
                        "time": event_time,
                        "run_text": run_text
                    })
                    
                    # Stop tracking once we have isolated the next 2 events
                    if len(upcoming_events) == 2:
                        break
        except ValueError:
            continue

    if upcoming_events:
        # Build the dynamic list elements inside the HTML template
        list_items_html = ""
        for event in upcoming_events:
            date_display = event["time"].strftime('%B %d')
            time_display = event["time"].strftime('%-I:%M %p') # Strips leading zero on Linux
            run_display = event["run_text"]
            
            list_items_html += f"        <div class='event-row'><strong>{date_display}</strong> at {time_display} — <em>{run_display}</em></div>\n"

        # Generate your identical clean HTML page layout
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
        print(f"Successfully generated index.html with {len(upcoming_events)} API events.")
    else:
        print("Could not find any future events in the API window.")

if __name__ == "__main__":
    main()
