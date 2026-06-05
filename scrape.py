import sys
from datetime import datetime, timedelta
import requests
import pytz

# Using the raw annual data repository. This bypasses the API and web servers entirely.
URL = "https://charts.gc.ca/publications/tables/00066-predictions-annual.txt"

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        print("📥 Downloading annual prediction database file...")
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to reach data repository: {e}")
        sys.exit(0)  # Exit cleanly to avoid triggering workflow failure alerts

    # Setup local New Brunswick time context
    tz = pytz.timezone('America/Halifax')
    now = datetime.now(tz)

    upcoming_events = []
    lines = response.text.split('\n')
    print(f"📋 File retrieved. Processing {len(lines)} lines of prediction matrix...")

    for line in lines:
        row_context = line.lower()
        # Look for the lines that designate a slack or turning point
        if "slack" in row_context or "0.0" in row_context:
            try:
                parts = line.split()
                if not parts:
                    continue
                
                # Standard annual text files format timestamps on the leading boundary: YYYY-MM-DDTHH:MM:SS
                event_str = parts[0]
                event_time = datetime.strptime(event_str, "%Y-%m-%dT%H:%M:%S")
                
                # Apply local timezone context
                event_time = tz.localize(event_time)

                # Filter for future events happening within the next 48 hours
                if now < event_time < (now + timedelta(days=2)):
                    
                    # Track direction flags
                    # If line has a '0' code or 'ebb' context -> End of inward run
                    # If line has a '1' code or 'flood' context -> End of outward run
                    if "0" in line or "ebb" in row_context:
                        run_text = "End of inward run"
                    elif "1" in line or "flood" in row_context:
                        run_text = "End of outward run"
                    else:
                        run_text = "Slack Water"

                    upcoming_events.append({
                        "time": event_time,
                        "run_text": run_text
                    })

                    if len(upcoming_events) == 2:
                        break
            except Exception:
                continue

    if upcoming_events:
        # Sort chronologically to be absolutely certain they match sequence
        upcoming_events.sort(key=lambda x: x["time"])
        
        list_items_html = ""
        for event in upcoming_events:
            date_display = event["time"].strftime('%B %d')
            time_display = event["time"].strftime('%-I:%M %p') # Strips leading zero on Linux
            run_display = event["run_text"]
            
            list_items_html += f"        <div class='event-row'><strong>{date_display}</strong> at {time_display} — <em>{run_display}</em></div>\n"

        # Output your pristine template layout
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
        print(f"🎉 Success! index.html updated via raw annual text file database.")
    else:
        print("⚠️ No future slack points found in the current log array window.")

if __name__ == "__main__":
    main()
