import sys
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import dateutil.parser

# Station 66 URL (Saint John / Reversing Falls data)
URL = "https://tides.gc.ca/en/stations/66"

def parse_tide_data(soup):
    now = datetime.now().astimezone() # Local time with timezone
    rows = soup.find_all('tr')
    
    slack_events = []
    
    for row in rows:
        text = row.get_text()
        # Filter for rows that indicate slack water (0.0 speed or explicitly labeled)
        if "Slack" in text or "0.0" in text:
            cells = row.find_all('td')
            if len(cells) >= 2:
                try:
                    time_str = cells[0].get_text().strip()
                    event_time = dateutil.parser.parse(time_str)
                    
                    # Only grab future slack waters
                    if event_time > now:
                        row_context = text.lower()
                        
                        # Determine run direction based on text context
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

    # Sort chronologically and isolate the next two closest events
    slack_events.sort(key=lambda x: x["time"])
    return slack_events[:2]

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        # Added explicit 10-second timeout to handle server hangs gracefully
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status() 
        
    except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
        print("⚠️ Connection timed out while reaching tides.gc.ca. Server may be down for maintenance.")
        sys.exit(0) # Exit cleanly so GitHub Actions doesn't trigger a build failure
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ A network error occurred: {e}")
        sys.exit(0)

    # Parse the HTML page
    soup = BeautifulSoup(response.text, 'html.parser')
    next_slacks = parse_tide_data(soup)
    
    # Build the HTML Block
    if not next_slacks:
        html_content = "<p>No upcoming slack water data found for today.</p>"
    else:
        html_content = "<h3>Upcoming Slack Water at Reversing Falls</h3>\n<ul style='list-style: none; padding: 0;'>\n"
        for slack in next_slacks:
            date_str = slack["time"].strftime("%B %d, %Y")
            
            # Linux-compatible '-%I' strips the leading zero (e.g., 1:15 PM instead of 01:15 PM)
            time_str = slack["time"].strftime("%-I:%M %p")
            direction_str = slack["direction"]
            
            html_content += f"  <li style='margin-bottom: 10px; font-size: 18px;'><strong>{date_str}</strong> at {time_str} - <em>{direction_str}</em></li>\n"
        html_content += "</ul>"
        
    # Write output to index.html for your GitHub Pages deployment
    with open("index.html", "w") as f:
        f.write(html_content)
        
    print("✅ index.html updated successfully with the next two slack tides.")

if __name__ == "__main__":
    main()
