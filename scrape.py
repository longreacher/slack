import sys
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import dateutil.parser

# Station 66 URL (Saint John / Reversing Falls data)
URL = "https://tides.gc.ca/en/stations/66"

def parse_tide_data(soup):
    # 1. Force the evaluation to use local Atlantic time context
    now = datetime.now().astimezone() 
    rows = soup.find_all('tr')
    
    slack_events = []
    
    print(f"DEBUG: System 'now' time evaluated as: {now}")
    print(f"DEBUG: Found {len(rows)} total rows in the page table.")

    for row in rows:
        text = row.get_text()
        row_context = text.lower()
        
        # Broaden the string match to capture variations of 'slack' or turning points
        if "slack" in row_context or "0.0" in row_context or "turn" in row_context:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                try:
                    # Look for a clean machine-readable time attribute first, fall back to text
                    time_cell = cells[0]
                    time_str = time_cell.get('data-iso') or time_cell.get_text().strip()
                    
                    event_time = dateutil.parser.parse(time_str)
                    
                    # Ensure event_time has a timezone attached so the comparison doesn't break
                    if event_time.tzinfo is None:
                        event_time = event_time.replace(tzinfo=now.tzinfo)
                    
                    # Log what we found to the GitHub Action output log
                    print(f"DEBUG: Found Slack Event at {event_time} | Context: {text.strip()}")

                    # Keep it if it's in the future
                    if event_time > now:
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
                except Exception as e:
                    print(f"DEBUG: Failed parsing row row due to: {e}")
                    continue

    # Sort chronologically and isolate the next two closest events
    slack_events.sort(key=lambda x: x["time"])
    print(f"DEBUG: Total upcoming events filtered: {len(slack_events)}")
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
