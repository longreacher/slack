import os
from datetime import datetime, date, timedelta

# Moving the template to the top level prevents all IndentationErrors
WORKFLOW_TEMPLATE = """name: Event-Driven Tide Automation

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
      with:
        token: ${{{{ secrets.AUTOMATION_TOKEN }}}}
        persist-credentials: false

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.x'

    - name: Run Scraping Script
      run: python scrape.py

    - name: Commit and Push index.html Changes
      run: |
        git config --local user.name "github-actions[bot]"
        git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
        
        git add index.html
        
        if ! git diff --cached --quiet; then
          git commit -m "Automated Update: Refreshed upcoming slack tide layouts"
          git push https://x-access-token:${{{{ secrets.AUTOMATION_TOKEN }}}}@github.com/${{{{ github.repository }}}}.git HEAD:main
        else
          echo "index.html is already up to date. No push required."
        fi
"""

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
    tomorrow = date.today()
    cron_list = []
    
    for dt, _ in tide_events:
        if dt.date() == tomorrow:
            # 1. Target Slack Time + 2 Minute
            local_trigger_time = dt + timedelta(minutes=2)
            
            # 2. Convert Local Atlantic Time to GitHub UTC (Add 3 hours for ADT)
            utc_trigger_time = local_trigger_time
            
            minute = utc_trigger_time.minute
            hour = utc_trigger_time.hour
            
            # Formats to standard GitHub Cron: 'minute hour * * *'
            cron_list.append(f"- cron: '{minute} {hour} * * *'")
            
    return cron_list

def write_workflow_file(cron_strings):
    if not cron_strings:
        cron_strings = ["- cron: '0 0 * * *'"] # Fallback

    cron_triggers = "\n    ".join(cron_strings)

    # Clean format injection away from function indents
    workflow_content = WORKFLOW_TEMPLATE.format(cron_triggers=cron_triggers)
    
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/tide_automation.yml", "w") as f:
        f.write(workflow_content)
    print("Successfully generated updated tide_automation.yml file.")

if __name__ == "__main__":
    events = load_tide_data("tides_2026.txt")
    crons = generate_cron_strings(events)
    write_workflow_file(crons)
