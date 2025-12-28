from __future__ import annotations

import json
import os
import uuid
from datetime import date
from typing import List, Dict, Any


def load_events(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_events(path: str, events: list) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)


def _validate_dates(start_date: str, end_date: str) -> None:
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as e:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.") from e
    if end < start:
        raise ValueError("end_date must be on or after start_date.")


def _generate_id(existing_ids: set[str]) -> str:
    while True:
        eid = uuid.uuid4().hex[:8]
        if eid not in existing_ids:
            return eid


def create_event(events: list, event_data: dict) -> dict:
    required = ["name", "location", "start_date", "end_date", "capacity", "price"]
    for key in required:
        if key not in event_data:
            raise ValueError(f"Missing required field '{key}' for event.")

    _validate_dates(event_data["start_date"], event_data["end_date"])

    try:
        capacity = int(event_data["capacity"])
        if capacity <= 0:
            raise ValueError
    except Exception:
        raise ValueError("Capacity must be a positive integer.")

    try:
        price = float(event_data["price"])
        if price < 0:
            raise ValueError
    except Exception:
        raise ValueError("Price must be a non-negative number.")

    existing_ids = {e.get("id") for e in events}
    eid = event_data.get("id") or _generate_id(existing_ids)
    if eid in existing_ids:
        raise ValueError(f"Event id '{eid}' already exists.")

    event = {
        "id": eid,
        "name": event_data["name"],
        "location": event_data["location"],
        "start_date": event_data["start_date"],
        "end_date": event_data["end_date"],
        "capacity": capacity,
        "price": price,
        "description": event_data.get("description", ""),
        "sessions": [],  # list of dicts
        "status": "scheduled",  # scheduled / cancelled
    }
    events.append(event)
    return event


def _find_event(events: list, event_id: str) -> dict:
    for e in events:
        if e.get("id") == event_id:
            return e
    raise ValueError(f"Event with id '{event_id}' not found.")


def update_event(events: list, event_id: str, updates: dict) -> dict:
    event = _find_event(events, event_id)

    if "start_date" in updates or "end_date" in updates:
        start = updates.get("start_date", event["start_date"])
        end = updates.get("end_date", event["end_date"])
        _validate_dates(start, end)

    if "capacity" in updates:
        try:
            cap = int(updates["capacity"])
            if cap <= 0:
                raise ValueError
            updates["capacity"] = cap
        except Exception:
            raise ValueError("Capacity must be a positive integer.")

    if "price" in updates:
        try:
            p = float(updates["price"])
            if p < 0:
                raise ValueError
            updates["price"] = p
        except Exception:
            raise ValueError("Price must be a non-negative number.")

    updates.pop("id", None)
    event.update(updates)
    return event


def add_session(events: list, event_id: str, session_data: dict) -> dict:
    event = _find_event(events, event_id)

    required = ["title", "speaker", "room", "capacity"]
    for key in required:
        if key not in session_data:
            raise ValueError(f"Missing required field '{key}' for session.")

    if "start_time" in session_data and "end_time" in session_data:
        try:
            sdate = session_data["start_time"][:10]
            edate = session_data["end_time"][:10]
            _validate_dates(sdate, edate)
        except Exception as e:
            raise ValueError("Invalid session start_time/end_time.") from e

        event_start = date.fromisoformat(event["start_date"])
        event_end = date.fromisoformat(event["end_date"])
        if date.fromisoformat(sdate) < event_start or date.fromisoformat(edate) > event_end:
            raise ValueError("Session dates must be within event dates.")

    try:
        cap = int(session_data["capacity"])
        if cap <= 0:
            raise ValueError
    except Exception:
        raise ValueError("Session capacity must be a positive integer.")

    existing_ids = {s.get("id") for s in event.get("sessions", [])}
    sid = session_data.get("id") or _generate_id(existing_ids)
    if sid in existing_ids:
        raise ValueError(f"Session id '{sid}' already exists for this event.")

    session = {
        "id": sid,
        "title": session_data["title"],
        "speaker": session_data["speaker"],
        "room": session_data["room"],
        "capacity": cap,
        "start_time": session_data.get("start_time"),
        "end_time": session_data.get("end_time"),
    }
    event.setdefault("sessions", []).append(session)
    return session


def list_sessions(events: list, event_id: str) -> list:
    event = _find_event(events, event_id)
    return event.get("sessions", [])
