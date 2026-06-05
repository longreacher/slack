import os
from datetime import datetime, date, timedelta

def load_tide_data(filepath="tides_2026.txt"):
    """
    Reads the formatted tide data from the text file.
    Returns a list of tuples: (datetime_obj, direction_code)
    """
    tide_events = []
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found. Please ensure the file exists.")
        return tide_events
        
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                datetime_str, code_str = line.split()
                dt = datetime.fromisoformat(datetime_str)
                code = int(code_str)
                tide_events.append((dt, code))
            except ValueError:
                # Skip any lines that don't match the expected format
                continue
    return tide_events

def get_day_label(event_date, target_date=None):
    """
    Returns 'Today', 'Tomorrow', or a formatted date string relative to target_date.
    """
    if target_date is None:
        target_date = date.today()
        
    if event_date == target_date:
        return "Today"
    elif event_date == target_date + timedelta(days=1):
        return "Tomorrow"
    else:
        # Formats future dates beautifully (e.g., "Monday, Sep 07")
        return event_date.strftime("%A, %b %d")

def display_tide_schedule(filepath="tides_2026.txt", show_all=False):
    """
    Parses and displays the tide schedule with dynamic 'Today' and 'Tomorrow' labels.
    """
    tide_events = load_tide_data(filepath)
    if not tide_events:
        return

    # Mapping codes to descriptive labels as specified by your repository rules
    status_mapping = {
        1: "End of outward run",
        0: "End of inward run"
    }

    current_dt = datetime.now()
    current_date = current_dt.date()

    print("=" * 65)
    print(f" REVERSING FALLS TIDE SCHEDULE (Generated on {current_dt.strftime('%Y-%m-%d %I:%M %p')})")
    print("=" * 65)

    upcoming_marked = False
    for dt, code in tide_events:
        event_date = dt.date()
        
        # By default, skip past dates to keep the console layout uncluttered
        if not show_all and event_date < current_date:
            continue
            
        day_label = get_day_label(event_date, current_date)
        time_str = dt.strftime("%I:%M %p")
        status_str = status_mapping.get(code, "Unknown status")
        
        # Place an arrow (->) next to the very next upcoming event
        prefix = "  "
        if not show_all and dt >= current_dt and not upcoming_marked:
            prefix = "-> "
            upcoming_marked = True
            
        print(f"{prefix}{day_label:<18} at {time_str:<8} | {status_str}")
    print("=" * 65)

if __name__ == "__main__":
    # Settings:
    # Set show_all=False to print only current & future tides (clean display)
    # Set show_all=True to output every row contained in tides_2026.txt
    display_tide_schedule("tides_2026.txt", show_all=False)
