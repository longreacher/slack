import os
from datetime import datetime, date, timedelta

def load_tide_data(filepath="tides_2026.txt"):
    tide_events = []
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return tide_events
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                datetime_str, code_str = line.split()
                dt = datetime.fromisoformat(datetime_str)
                tide_events.append((dt, int(code_str)))
            except ValueError: continue
    return tide_events

def generate_cron_strings(tide_events):
    tomorrow = date.today() + timedelta(days=1)
    cron_list = []
    
    for dt, _ in tide_events:
        if dt.date() == tomorrow:
            # 1. Target Slack Time + 1 Minute
            local_trigger_time = dt + timedelta(minutes=1)
            
            # 2. Convert Local Atlantic Time to GitHub UTC (Add 3 hours for ADT)
            utc_trigger_time = local_trigger_time + timedelta(hours=3)
            
            minute = utc_trigger_time.minute
            hour = utc_trigger_time.hour
            
            # Formats to standard GitHub Cron: 'minute hour * * *'
            cron_list.append(f"- cron: '{minute} {hour} * * *'")
            
    return cron_list

def write_workflow_file(cron_strings):
    if not cron_strings:
        cron_strings = ["- cron: '0 0 * * *'"] # Fallback

    cron_triggers = "\n    ".join(cron_strings)

    workflow_template = f"""name: Event-Driven Tide Automation

on:
  schedule:
    # Automatically scheduled target UTC times for tomorrow:
    {cron_triggers}
  workflow_dispatch:

jobs:
  execute_automation:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.x'

    - name: Run Scraping Script
      run: python scrape.py
"""
    
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/tide_automation.yml", "w") as f:
        f.write(workflow_template)
    print("Successfully generated updated tide_automation.yml file.")

if __name__ == "__main__":
    events = load_tide_data("tides_2026.txt")
    crons = generate_cron_strings(events)
    write_workflow_file(crons)
