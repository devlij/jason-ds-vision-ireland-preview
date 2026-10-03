#!/usr/bin/env python3
"""One fresh Open-Meteo retrieval per scene. Never batch-share a timestamp.

Existing evidence files are kept. The Ireland seed list is empty until a still is published.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "weather"
MONTHS = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

# Later scenes append here. Do not re-list a scene that already has a file.
# Pins are the public viewpoint, not a surveyed tripod mark.
# Republic of Ireland only. Northern Ireland belongs to the UK gallery.
SCENES: list[tuple[str, str, str, float, float, str]] = [
    # IE-01-001–010 Candidate stills, 30 September 2026. Not surveyed tripod marks.
    ("IE-01-001", "Trinity College", "Dublin", 53.34440, -6.25731, "Europe/Dublin"),
    ("IE-01-002", "Ha'penny Bridge", "Dublin", 53.34630, -6.26320, "Europe/Dublin"),
    ("IE-01-003", "Temple Bar", "Dublin", 53.34542, -6.26390, "Europe/Dublin"),
    ("IE-01-004", "Dublin Castle", "Dublin", 53.34285, -6.26740, "Europe/Dublin"),
    ("IE-01-005", "St Stephen's Green", "Dublin", 53.33860, -6.26000, "Europe/Dublin"),
    ("IE-01-006", "Custom House", "Dublin", 53.34770, -6.25280, "Europe/Dublin"),
    ("IE-01-007", "Guinness Storehouse", "Dublin", 53.34180, -6.28670, "Europe/Dublin"),
    ("IE-01-008", "Wellington Monument", "Dublin", 53.34905, -6.30314, "Europe/Dublin"),
    ("IE-01-009", "Howth Harbour", "Howth", 53.38980, -6.07020, "Europe/Dublin"),
    ("IE-01-010", "Killiney Hill", "Killiney", 53.26558, -6.11184, "Europe/Dublin"),
    # IE-01-031–035 Candidate stills. Catalogue pins, not surveyed tripod marks.
    ("IE-01-031", "Poll na bPéist", "Kilronan", 53.139, -9.7371, "Europe/Dublin"),
    ("IE-01-032", "Muckross House", "Killarney", 52.026, -9.4933, "Europe/Dublin"),
    ("IE-01-033", "Ross Castle", "Killarney", 52.0414, -9.5313, "Europe/Dublin"),
    ("IE-01-034", "Skellig Michael", "Portmagee", 52.7712, -10.5407, "Europe/Dublin"),
    ("IE-01-035", "Gallarus Oratory", "Ballydavid", 52.1726, -10.2184, "Europe/Dublin"),
]


def existing_stamps() -> set[str]:
    stamps = set()
    if not OUT.exists():
        return stamps
    for path in OUT.glob("IE-*.json"):
        data = json.loads(path.read_text())
        stamps.add(data["retrieval_timestamp"])
    return stamps


def fetch_one(
    entry_id: str,
    site: str,
    city: str,
    lat: float,
    lon: float,
    tz_name: str,
    stamps: set[str],
) -> dict:
    tz = ZoneInfo(tz_name)
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code,cloud_cover,wind_speed_10m,is_day,precipitation",
        "daily": "sunrise,sunset",
        "timezone": tz_name,
        "forecast_days": 1,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    time.sleep(2.0)
    request_started = datetime.now(tz)
    req = urllib.request.Request(url, headers={"User-Agent": "jasons-vision-ireland/1.0"})
    body = None
    last_err: Exception | None = None
    for _attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                body = resp.read()
            break
        except Exception as err:
            last_err = err
            time.sleep(2.0)
    if body is None:
        raise SystemExit(f"{entry_id} Open-Meteo failed: {last_err}")
    retrieval = datetime.now(tz)
    stamp = retrieval.isoformat(timespec="seconds")
    if stamp in stamps:
        raise SystemExit(f"{entry_id} retrieval second collided: {stamp}")
    payload = json.loads(body)
    current = payload["current"]
    daily = payload["daily"]
    sunrise = daily["sunrise"][0]
    is_day = current["is_day"]
    daynight = "night" if is_day == 0 or stamp[11:16] < sunrise[11:16] else "day"
    record = {
        "entry_id": entry_id,
        "site": site,
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "model_latitude": payload.get("latitude"),
        "model_longitude": payload.get("longitude"),
        "provider": "Open-Meteo",
        "retrieval_timestamp": stamp,
        "retrieval_display": (
            f"{retrieval.day} {MONTHS[retrieval.month]} {retrieval.year} "
            f"{retrieval.strftime('%H:%M:%S')} {tz_name}"
        ),
        "request_started": request_started.isoformat(timespec="seconds"),
        "model_time": current["time"],
        "model_interval_seconds": current.get("interval", 900),
        "timezone": payload.get("timezone", tz_name),
        "temperature_2m": current["temperature_2m"],
        "weather_code": current["weather_code"],
        "cloud_cover": current["cloud_cover"],
        "wind_speed_10m": current["wind_speed_10m"],
        "is_day": is_day,
        "precipitation": current["precipitation"],
        "sunrise": sunrise,
        "sunset": daily["sunset"][0],
        "model_valid_hour_start": retrieval.strftime("%Y-%m-%dT%H:00"),
        "scenario_label": (
            f"{retrieval.day} {MONTHS[retrieval.month]} {retrieval.year} · "
            f"{retrieval.strftime('%H:%M')} {tz_name}"
        ),
        "daynight": daynight,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{entry_id}.json").write_text(json.dumps(record, indent=2) + "\n")
    stamps.add(stamp)
    print(entry_id, stamp, "daynight", daynight, "code", record["weather_code"])
    return record


def main() -> None:
    stamps = existing_stamps()
    for row in SCENES:
        if (OUT / f"{row[0]}.json").exists():
            print(f"keep {row[0]}")
            continue
        fetch_one(*row, stamps)


if __name__ == "__main__":
    main()
