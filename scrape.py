import sys
from datetime import datetime, timedelta
import requests
import pytz

# Official Government OGC Geospatial API endpoint for Station 00066 (Saint John / Reversing Falls)
# This handles automated background cloud requests instantly without firewalls or proxies.
URL = "https://geoweb-api.dfo-mpo.gc.ca/api/features/collections/predictions-currents/items"
PARAMS = {
    "id-station": "00066",
    "limit": "50",  # Pull enough rows to safely capture the next 48 hours
    "sortby": "date-heure-event"
}

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        print("📥 Fetching clean dataset from official DFO Geospatial API...")
        response = requests.get(URL, headers=headers, params=PARAMS, timeout=15)
        response.raise_for_status()
        json_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API connection hurdle: {e}")
        sys.exit(0) # Exit cleanly to avoid workflow build errors

    # Setup local New Brunswick time context
    tz = pytz.timezone('America/Halifax')
    now = datetime.now(tz)

    upcoming_events = []
    features = json_data.get("features", [])
    print(f"📋 Received data grid. Processing {len(features)} data features...")

    for feature in features:
        props = feature.get("properties", {})
        event_str = props.get("date-heure-event")       # e.g., "2026-06-05T17:51:00Z"
        status_code = str(props.get("code-status", "")) # Matches your 0 or 1 mapping
        
        if not event_str:
            continue
            
        try:
            # Parse the API's standard ISO string as UTC, then translate to Atlantic time
            utc_time = datetime.strptime(event_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            event_time = utc_time.astimezone(tz)
            
            # Filter for events happening in the future
            if event_time > now:
                # 0 = End of inward run (turning to ebb)
                # 1 = End of outward run (turning to flood)
                if "0" in status_code:
                    run_text = "End of inward run"
                elif "1" in status_code:
                    run_text = "End of outward run"
                else:
                    # Fallback check on text description if status code changes
                    desc = props.get("description-evenement-en", "").lower()
                    if "slack" in desc:
                        if "ebb" in desc:
                            run_text = "End of inward run"
                        elif "flood" in desc:
                            run_text = "End of outward run"
                        else:
                            run_text = "Slack Water"
                    else:
                        continue # Skip non-slack entries (like maximum flow entries)

                upcoming_events.append({
                    "time": event_time,
                    "run_text": run_text
                })
        except Exception:
            continue

    # Ensure everything is in perfect chronological order and isolate the top two
    upcoming_events.sort(key=lambda x: x["time"])
    next_two = upcoming_events[:2]

    if next_two:
        # Build the dynamic list rows inside the HTML template
        list_items_html = ""
        for event in next_two:
            date_display = event["time"].strftime('%B %d')
            time_display = event["time"].strftime('%-I:%M %p') # Strips leading zero on Linux
            run_display = event["run_text"]
            
            list_items_html += f"        <div class='event-row'><strong>{date_display}</strong> at {time_display} — <em>{run_display}</em></div>\n"

        # Generate your identical clean HTML layout
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
        print(f"🎉 Success! Generated index.html with {len(next_two)} tracking events via OGC API.")
    else:
        print("⚠️ Could not locate any upcoming slack events inside the API payload window.")

if __name__ == "__main__":
    main()
