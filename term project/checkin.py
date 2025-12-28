from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict, Any


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def check_in_attendee(registrations: list, registration_id: str) -> dict:
    for r in registrations:
        if r.get("id") == registration_id or r.get("confirmation_code") == registration_id:
            if r.get("status") in {"cancelled", "waitlisted"}:
                raise ValueError("Cannot check in cancelled or waitlisted registration.")
            r["status"] = "checked-in"
            r["checkin_timestamp"] = _now_iso()
            r["updated_at"] = r["checkin_timestamp"]
            return r
    raise ValueError("Registration not found.")


def list_checked_in_attendees(registrations: list, event_id: str) -> list:
    return [
        r
        for r in registrations
        if r.get("event_id") == event_id and r.get("status") == "checked-in"
    ]


def generate_badge(attendee: dict, registration: dict, directory: str) -> str:
    os.makedirs(directory, exist_ok=True)
    filename = f"badge_{registration['id']}.txt"
    path = os.path.join(directory, filename)

    lines = [
        "==============================",
        "        EVENT BADGE",
        "==============================",
        f"Name        : {attendee.get('name')}",
        f"Organization: {attendee.get('organization', '')}",
        f"Ticket Type : {registration.get('ticket_type')}",
        f"Confirmation: {registration.get('confirmation_code')}",
        "",
        "Sessions:",
    ]
    sessions = registration.get("sessions", [])
    if sessions:
        for sid in sessions:
            lines.append(f"  - Session ID: {sid}")
    else:
        lines.append("  (None assigned)")

    lines.append("==============================")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path


def session_attendance(registrations: list, event_id: str, session_id: str) -> dict:
    registered = 0
    checked_in = 0
    for r in registrations:
        if r.get("event_id") != event_id:
            continue
        sessions = r.get("sessions", [])
        if session_id in sessions:
            if r.get("status") in {"confirmed", "checked-in"}:
                registered += 1
            if r.get("status") == "checked-in":
                checked_in += 1
    return {
        "event_id": event_id,
        "session_id": session_id,
        "registered": registered,
        "checked_in": checked_in,
    }
