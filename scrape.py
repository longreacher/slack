import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

url = "https://tides.gc.ca/en/stations/00066/predictions/annual"

def main():
    # Fetch the page
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # The station is in New Brunswick, which uses Atlantic Time (AST/ADT)
    tz = pytz.timezone('America/Halifax')
    now = datetime.now(tz).replace(tzinfo=None)

    next_event = None
    direction = None

    # Parse table rows for the data
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            date_str = tds[0].get_text(strip=True)
            dir_str = tds[1].get_text(strip=True)
            
            try:
                # Parse times structured like '2026-06-04T15:03:00'
                event_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                
                # Find the very first event that is greater than the current time
                if event_time > now:
                    next_event = event_time
                    direction = dir_str
                    break
            except ValueError:
                continue

    if next_event:
        # Check if direction is 0 (Outward) or 1 (Inward)
        if "0" in direction:
            run_text = "End of outward run"
        elif "1" in direction:
            run_text = "End of inward run"
        else:
            run_text = "Unknown direction"

        # Generate the HTML page
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Next Tide Event - Reversing Falls</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding-top: 10vh; background-color: #f4f4f9; color: #333; }}
        .container {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; }}
        h1 {{ margin-top: 0; font-size: 1.5rem; color: #555; }}
        .event {{ font-size: 2.5rem; font-weight: bold; color: #0056b3; margin: 20px 0; }}
        .time {{ font-size: 1.5rem; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Next Event at Reversing Falls (00066)</h1>
        <div class="event">{run_text}</div>
        <div class="time">{next_event.strftime('%B %d, %Y at %I:%M %p')}</div>
    </div>
</body>
</html>"""

        with open("index.html", "w") as f:
            f.write(html_content)
        print(f"Successfully generated index.html: {run_text} at {next_event}")
    else:
        print("Could not find a future event.")

if __name__ == "__main__":
    main()
