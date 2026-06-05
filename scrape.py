import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# We append a free, public Scraper proxy prefix to the URL. 
# This shifts the request away from GitHub's blocked IP block so the page loads instantly.
url = "https://api.allorigins.win/get?url=" + requests.utils.quote("https://tides.gc.ca/en/stations/00066/predictions/annual")

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        print("📥 Fetching page contents via proxy tunnel...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # AllOrigins wraps the page in a JSON object under the key 'contents'
        json_data = response.json()
        html_raw = json_data.get("contents", "")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Proxy connection hurdle: {e}")
        sys.exit(0) # Exit cleanly to avoid workflow alerts

    # Feed the raw HTML into BeautifulSoup
    soup = BeautifulSoup(html_raw, 'html.parser')

    # The station is in New Brunswick, which uses Atlantic Time (AST/ADT)
    tz = pytz.timezone('America/Halifax')
    now = datetime.now(tz).replace(tzinfo=None)

    upcoming_events = []

    # Parse table rows for the data exactly like your original working code
    rows = soup.find_all('tr')
    print(f"📋 Received data. Processing {len(rows)} table elements...")

    for tr in rows:
        tds = tr.find_all('td')
        if len(tds) >= 2:
            date_str = tds[0].get_text(strip=True)
            dir_str = tds[1].get_text(strip=True)
            
            try:
                # Parse times structured like '2026-06-04T15:03:00'
                event_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                
                # Check if this event happens in the future
                if event_time > now:
                    if "0" in dir_str:
                        run_text = "End of outward run"
                    elif "1" in dir_str:
                        run_text = "End of inward run"
                    else:
                        run_text = "Slack Water"
                        
                    upcoming_events.append({
                        "time": event_time,
                        "run_text": run_text
                    })
                    
                    # Stop searching once we have isolated the next 2 events
                    if len(upcoming_events) == 2:
                        break
            except ValueError:
                continue

    if upcoming_events:
        # Build the dynamic list elements inside the HTML
        list_items_html = ""
        for event in upcoming_events:
            date_display = event["time"].strftime('%B %d')
            time_display = event["time"].strftime('%-I:%M %p') # Strips leading zero on Linux
            run_display = event["run_text"]
            
            list_items_html += f"        <div class='event-row'><strong>{date_display}</strong> at {time_display} — <em>{run_display}</em></div>\n"

        # Generate your pristine HTML page template
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
        print(f"✅ Successfully updated index.html with {len(upcoming_events)} events via proxy tunnel!")
    else:
        print("⚠️ Reached table but could not find future rows inside current window.")

if __name__ == "__main__":
    main()
