import json
import logging
import os
import re
from pathlib import Path
from typing import Callable

import requests
from flask import Flask, Response
from icalendar import Calendar

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OPTIONS_PATH = Path("/data/options.json")
DEFAULT_UPSTREAM = "https://www.glynschool.org/calendar/events.ics"
TERM_KEYWORDS = [
    "term begins",
    "term ends",
    "christmas break",
    "easter break",
    "half term",
    "bank holiday",
]
YEAR_NOT_SEVEN_PATTERN = re.compile(r"^year\s+(1|2|3|4|5|6|8|9|10|11|12|13)\b", re.IGNORECASE)

app = Flask(__name__)


def load_options() -> dict:
    if OPTIONS_PATH.exists():
        try:
            with OPTIONS_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read options.json: %s", exc)
    return {}


def get_upstream_url() -> str:
    options = load_options()
    upstream = options.get("upstream_url") if isinstance(options, dict) else None
    if not upstream:
        upstream = os.getenv("UPSTREAM_URL", DEFAULT_UPSTREAM)
    return upstream


def fetch_calendar(url: str) -> Calendar:
    logger.info("Fetching calendar from %s", url)
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return Calendar.from_ical(response.content)


def is_week_event(summary: str) -> bool:
    normalized = summary.strip().lower()
    return normalized in {"week 1", "week 2"}


def matches_term_keyword(summary: str) -> bool:
    lowered = summary.lower()
    return any(keyword in lowered for keyword in TERM_KEYWORDS)


def is_year_not_seven(summary: str) -> bool:
    return bool(YEAR_NOT_SEVEN_PATTERN.search(summary))


def keep_year7_event(component) -> bool:
    summary = str(component.get("SUMMARY", ""))
    if is_week_event(summary):
        return True
    if matches_term_keyword(summary):
        return False
    if is_year_not_seven(summary):
        return False
    return True


def keep_term_date_event(component) -> bool:
    summary = str(component.get("SUMMARY", ""))
    return matches_term_keyword(summary)


def build_filtered_calendar(calendar: Calendar, predicate: Callable) -> bytes:
    new_calendar = Calendar()
    for header in ["PRODID", "VERSION", "CALSCALE", "X-WR-CALNAME", "X-WR-TIMEZONE"]:
        if header in calendar:
            new_calendar.add(header, calendar.get(header))
    for component in calendar.walk():
        if component.name == "VEVENT":
            if predicate(component):
                new_calendar.add_component(component)
        elif component.name not in {"VCALENDAR"}:
            new_calendar.add_component(component)
    return new_calendar.to_ical()


def serve_filtered_calendar(predicate: Callable) -> Response:
    upstream_url = get_upstream_url()
    calendar = fetch_calendar(upstream_url)
    filtered = build_filtered_calendar(calendar, predicate)
    return Response(filtered, mimetype="text/calendar")


@app.route("/glyn_year7.ics", methods=["GET"])
def glyn_year7():
    return serve_filtered_calendar(keep_year7_event)


@app.route("/glyn_term_dates.ics", methods=["GET"])
def glyn_term_dates():
    return serve_filtered_calendar(keep_term_date_event)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8099"))
    app.run(host="0.0.0.0", port=port)
