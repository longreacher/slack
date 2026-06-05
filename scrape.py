import sys
from datetime import datetime, timedelta
import requests
import dateutil.parser

# Station 00066 (Saint John / Reversing Falls) raw annual text predictions data
# This endpoint bypasses the main web server's strict GitHub firewall blocks
URL = "https://tides.gc.ca/en/stations/00066/predictions/annual/text"

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        print("📥 Fetching raw annual tide data payload...")
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to reach data repository: {e}")
        sys.exit(0)

    now = datetime.now().astimezone()
    slack_events = []

    # Process the raw text line by line
    lines = response.text.split('\n')
    print(f"📋 Processing {len(lines)} lines of prediction data...")

    for line in lines:
        row_context = line.lower()
        # Look for lines indicating a slack/turning point
        if "slack" in row_context or "0.0" in row_context or "turn" in row_context:
            try:
                # Extract the timestamp. The text format generally leads with a standard ISO string
                # split by tabs or spaces. We grab the first chunk that looks like a date.
                parts = line.split()
                if not parts:
                    continue
                
                # Parse the date string from the row line
                event_time = dateutil.parser.parse(parts[0])
                
                # Sync timezones for comparison
                if event_time.tzinfo is None:
                    event_time = event_time.replace(tzinfo=now.tzinfo)

                # Keep future events within a reasonable window (next 48 hours)
                if now < event_time < (now + timedelta(days=2)):
                    if "flood" in row_context or "inward" in row_context:
                        direction = "End of outward run"
                    elif "ebb" in row_context or "outward" in row_context:
                        direction = "End of inward run"
                    else:
                        direction = "Slack Water"

                    slack_events.append({
                        "time": event_time,
                        "direction": direction
                    })
            except Exception:
                continue

    # Sort and pick the closest two
    slack_events.sort(key=lambda x: x["time"])
    next_slacks = slack_events[:2]

    # Build the HTML output
    if not next_slacks:
        print("⚠️ Match arrays came up empty.")
        html_content = "<p>No upcoming slack water data found for the current window.</p>"
    else:
        html_content = "<h3>Upcoming Slack Water at Reversing Falls</h3>\n<ul style='list-style: none; padding: 0;'>\n"
        for slack in next_slacks:
            date_str = slack["time"].strftime("%B %d, %Y")
            time_str = slack["time"].strftime("%-I:%M %p")
            direction_str = slack["direction"]
            html_content += f"  <li style='margin-bottom: 10px; font-size: 18px;'><strong>{date_str}</strong> at {time_str} - <em>{direction_str}</em></li>\n"
        html_content += "</ul>"
        print(f"🎯 Successfully found {len(next_slacks)} upcoming events.")

    # Commit to file
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    main()
