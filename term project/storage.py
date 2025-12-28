from __future__ import annotations

import json
import os
import shutil
from typing import List, Dict, Any, Tuple


def _data_dir(base_dir: str) -> str:
    return os.path.join(base_dir, "data")


def load_state(base_dir: str) -> tuple[list, list, list]:
    ddir = _data_dir(base_dir)
    events_path = os.path.join(ddir, "events.json")
    attendees_path = os.path.join(ddir, "attendees.json")
    registrations_path = os.path.join(ddir, "registrations.json")

    events: list = []
    attendees: list = []
    registrations: list = []

    if os.path.exists(events_path):
        with open(events_path, "r", encoding="utf-8") as f:
            events = json.load(f)

    if os.path.exists(attendees_path):
        with open(attendees_path, "r", encoding="utf-8") as f:
            attendees = json.load(f)

    if os.path.exists(registrations_path):
        with open(registrations_path, "r", encoding="utf-8") as f:
            registrations = json.load(f)

    return events, attendees, registrations


def save_state(base_dir: str, events: list, attendees: list, registrations: list) -> None:
    ddir = _data_dir(base_dir)
    os.makedirs(ddir, exist_ok=True)

    events_path = os.path.join(ddir, "events.json")
    attendees_path = os.path.join(ddir, "attendees.json")
    registrations_path = os.path.join(ddir, "registrations.json")

    with open(events_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    with open(attendees_path, "w", encoding="utf-8") as f:
        json.dump(attendees, f, indent=2, ensure_ascii=False)

    with open(registrations_path, "w", encoding="utf-8") as f:
        json.dump(registrations, f, indent=2, ensure_ascii=False)


def backup_state(base_dir: str, backup_dir: str) -> list[str]:
    os.makedirs(backup_dir, exist_ok=True)
    ddir = _data_dir(base_dir)

    from datetime import datetime
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    created: list[str] = []
    for name in ("events.json", "attendees.json", "registrations.json"):
        src = os.path.join(ddir, name)
        if os.path.exists(src):
            dest = os.path.join(backup_dir, f"{stamp}-{name}")
            shutil.copy2(src, dest)
            created.append(dest)
    return created


def validate_registration(registration: dict) -> bool:
    required_keys = {
        "id",
        "event_id",
        "attendee_id",
        "ticket_type",
        "confirmation_code",
        "payment_method",
        "payment_status",
        "status",
        "created_at",
    }
    if not isinstance(registration, dict):
        return False
    if not required_keys.issubset(registration.keys()):
        return False
    return True
