import os
from datetime import datetime, date

def generate_slack_dashboard():
    # --- CHANGED: Pointing back to your correct data asset file ---
    filepath = "tides_2026.txt"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    # Target today's calendar date
    today = date.today()
    slack_events = []

    # Read and parse your specific file structure
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            # Split by tabs
            parts = line.split("\t")
            if len(parts) < 2:
                continue
                
            datetime_str = parts[0].strip()   # e.g., "2026-06-07T07:36:00"
            state_val = parts[1].strip()      # e.g., "1" or "0"
            
            try:
                # Parse the ISO style timestamp containing the 'T'
                dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue

            # Isolate today's specific 24-hour window
            if dt.date() == today:
                # --- CHANGED: Map binary 1 and 0 values to custom labels ---
                if state_val == "1":
                    display_label = "End of inward run"
                    text_color = "#1b5e20"  # Deep Forest Green
                    bg_color = "#e8f5e9"
                elif state_val == "0":
                    display_label = "End of Outward Run"
                    text_color = "#b71c1c"  # Deep Nautical Red
                    bg_color = "#ffebee"
                else:
                    continue  # Skip any unexpected records

                slack_events.append({
                    "dt_obj": dt,
                    "time": dt.strftime("%I:%M %p").lstrip("0"),
                    "label": display_label,
                    "text_color": text_color,
                    "bg_color": bg_color
                })

    # Sort sequentially by actual datetime objects to guarantee chronologic order
    slack_events.sort(key=lambda x: x["dt_obj"])

    # Generate HTML cards dynamically
    events_html = ""
    if slack_events:
        for event in slack_events:
            events_html += f"""
            <div class="event-card" style="background-color: {event['bg_color']}; border-left: 5px solid {event['text_color']};">
                <div class="event-time">{event['time']}</div>
                <div class="event-label" style="color: {event['text_color']};">{event['label']}</div>
            </div>
            """
    else:
        events_html = "<p style='color:#666; font-style:italic; text-align:center;'>No slack water events remaining today.</p>"

    # Build the tight layout with minimized top whitespace
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Daily Slack Water Status</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 5px 5px;
            background-color: #f4f6f9;
            color: #333;
        }}
        .container {{
            max-width: 500px;
            margin: 5px auto; /* Keeps the container tightly hugging the top */
            background: #ffffff;
            padding: 5px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }}
        h2 {{
            margin-top: 0; /* Drops browser default native title spacer */
            margin-bottom: 5px;
            font-size: 1.4rem;
            color: #1a237e;
            text-align: center;
        }}
        .date-sub {{
            font-size: 1rem;
            color: #666;
            margin-bottom: 10px;
            text-align: center;
        }}
        .event-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .event-card {{
            padding: 7px 9px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .event-time {{
            font-size: 1.1rem;
            font-weight: bold;
            color: #212121;
            min-width: 95px;
        }}
        .event-label {{
            font-size: 1.05rem;
            font-weight: bold;
            flex-grow: 1;
            padding-left: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Slack Water @ Reversing Falls</h2>
        <div class="date-sub">{today.strftime('%A, %B %d')}</div>
        <div class="event-list">
            {events_html}
        </div>
    </div>
</body>
</html>
"""

    with open("index.html", "w") as f:
        f.write(html_content)
    print(f"Successfully compiled stream guide using tides_2026.txt for {today}.")

if __name__ == "__main__":
    generate_slack_dashboard()
