import os
from datetime import datetime, date

def generate_slack_dashboard():
    # Use your source data file (adjust filename if your slack data file has a unique name)
    filepath = "Westfield Tides.txt"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    # Target today's calendar date
    today = date.today()
    slack_events = []

    # Read and extract today's milestones
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            parts = line.split("\t")
            if len(parts) < 3:
                continue
                
            datetime_str = parts[0].strip()   # e.g., "2026-06-25 08:42"
            height_val = float(parts[1].strip()) # e.g., 0.85
            state = parts[2].strip().upper()  # e.g., "HIGHTIDE" or "LOWTIDE"
            
            try:
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            # Isolate today's specific 24-hour window
            if dt.date() == today:
                # Map the states to your custom stream direction definitions
                if "HIGH" in state:
                    display_label = "End of inward run"
                    text_color = "#1b5e20"  # Deep Forest Green
                    bg_color = "#e8f5e9"
                elif "LOW" in state:
                    display_label = "End of Outward Run"
                    text_color = "#b71c1c"  # Deep Nautical Red
                    bg_color = "#ffebee"
                else:
                    continue  # Skip raw transitional points like 'FALLING' or 'RISING'

                slack_events.append({
                    "time": dt.strftime("%I:%M %p").lstrip("0"),
                    "label": display_label,
                    "height": f"{height_val:.2f}m",
                    "text_color": text_color,
                    "bg_color": bg_color
                })

    # Sort sequentially by time just in case your dataset rows are out of order
    slack_events.sort(key=lambda x: datetime.strptime(x["time"], "%I:%M %p") if ":" in x["time"] else x["time"])

    # Generate HTML list items dynamically
    events_html = ""
    if slack_events:
        for event in slack_events:
            events_html += f"""
            <div class="event-card" style="background-color: {event['bg_color']}; border-left: 5px solid {event['text_color']};">
                <div class="event-time">{event['time']}</div>
                <div class="event-label" style="color: {event['text_color']};">{event['label']}</div>
                <div class="event-height">Height: {event['height']}</div>
            </div>
            """
    else:
        events_html = "<p style='color:#666; font-style:italic;'>No slack water events recorded for today.</p>"

    # Build the tight layout with reduced top whitespace
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Daily Slack Water Status</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 10px 10px; /* Tight top padding */
            background-color: #f4f6f9;
            color: #333;
        }}
        .container {{
            max-width: 500px;
            margin: 5px auto; /* Minimal gap at top of browser */
            background: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            text-align: center;
        }}
        h2 {{
            margin-top: 0; /* Erases default browser header spacing */
            margin-bottom: 5px;
            font-size: 1.4rem;
            color: #1a237e;
        }}
        .date-sub {{
            font-size: 1rem;
            color: #666;
            margin-bottom: 20px;
        }}
        .event-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            text-align: left;
        }}
        .event-card {{
            padding: 14px 18px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .event-time {{
            font-size: 1.1rem;
            weight: 700;
            font-weight: bold;
            color: #212121;
            min-width: 85px;
        }}
        .event-label {{
            font-size: 1.05rem;
            font-weight: bold;
            flex-grow: 1;
            padding-left: 10px;
        }}
        .event-height {{
            font-size: 0.9rem;
            color: #555;
            text-align: right;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Slack Water Stream Guide</h2>
        <div class="date-sub">{today.strftime('%A, %B %d, %Y')}</div>
        <div class="event-list">
            {events_html}
        </div>
    </div>
</body>
</html>
"""

    with open("index.html", "w") as f:
        f.write(html_content)
    print(f"Successfully compiled static stream guide for {today}.")

if __name__ == "__main__":
    generate_slack_dashboard()
