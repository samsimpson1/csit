#!/usr/bin/env uv run

# /// script
# dependencies = [
#   "Jinja2==3.1.6",
#   "PyYAML==6.0.3"
# ]
# ///

from subprocess import run
from os import makedirs
from os.path import join
from datetime import datetime
from hashlib import md5
from jinja2 import FileSystemLoader, Environment
from yaml import safe_load

env = Environment(loader=FileSystemLoader("templates"))


def sort_events(events):
    return sorted(events, key=lambda e: e["date"])


def render_calendar(events):
    ics_timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")

    template = env.get_template("calendar.ics.j2")
    return template.render(
        events=events,
        csit_hostname="samsimpson1.github.io",
        csit_name="CSIT",
        ics_timestamp=ics_timestamp,
    ).replace("\n", "\r\n")


def parse_dates(dates: str):
    events = []

    for date_line in dates.splitlines():
        date_line_s = date_line.strip()
        date_line_parts = date_line_s.split(" ")
        date_str = date_line_parts[0]
        date = datetime.strptime(date_str, "%Y-%m-%d")
        event_name = " ".join(date_line_parts[1:])
        uid = md5(date_line_s.encode()).hexdigest()

        events.append(
            {
                "date": date,
                "ics_date": date.strftime("%Y%m%d"),
                "name": event_name,
                "uid": uid,
            }
        )
    return sort_events(events)


def load_calendars_config():
    with open("calendars.yaml", "r") as f:
        return safe_load(f)


def build_calendar_events():
    calendars = {}
    config = load_calendars_config()

    for calendar_id in config:
        print(f"Building calendar events {calendar_id}...")
        calendar = config[calendar_id]
        dates = ""
        if "file" in calendar:
            with open(join("sources", calendar["file"]), "r") as f:
                dates = f.read()
        elif "command" in calendar:
            result = run(
                join("sources", calendar["command"]),
                capture_output=True,
                text=True,
                shell=True,
            )
            if result.returncode != 0:
                print(
                    f"Error running command for calendar {calendar_id}: {result.stderr}"
                )
                continue
            dates = result.stdout.strip()

        if dates != "":
            events = parse_dates(dates)
            calendars[calendar_id] = events

    for calendar_id in config:
        calendar = config[calendar_id]
        if "combine" in calendar:
            events = []
            for source in calendar["combine"]:
                events.extend(calendars[source])
            calendars[calendar_id] = sort_events(events)

    for c in calendars:
        print(f"{c}: {len(calendars[c])} events")

    return calendars


def render_and_write_calendar(id, events):
    rendered = render_calendar(events)
    with open(join("output", f"{id}.ics"), "w") as f:
        f.write(rendered)


def render_and_write_index():
    calendars = load_calendars_config()
    template = env.get_template("index.html.j2")
    rendered = template.render(calendars=calendars)
    with open(join("output", "index.html"), "w") as f:
        f.write(rendered)

if __name__ == "__main__":
    makedirs("output", exist_ok=True)
    
    render_and_write_index()

    calendars = build_calendar_events()

    for calendar_id in calendars:
        print(f"Rendering calendar {calendar_id}...")
        render_and_write_calendar(calendar_id, calendars[calendar_id])
