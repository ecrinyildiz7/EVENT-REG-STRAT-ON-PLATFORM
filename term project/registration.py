from __future__ import annotations

import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _find_event(events: list, event_id: str) -> dict:
    for e in events:
        if e.get("id") == event_id:
            return e
    raise ValueError(f"Event with id '{event_id}' not found.")


def _event_confirmed_registrations(registrations: list, event_id: str) -> list:
    return [
        r
        for r in registrations
        if r.get("event_id") == event_id and r.get("status") in {"confirmed", "checked-in"}
    ]


def _event_waitlist(registrations: list, event_id: str) -> list:
    return [
        r
        for r in registrations
        if r.get("event_id") == event_id and r.get("status") == "waitlisted"
    ]


def create_registration(
    registrations: list,
    registration_data: dict,
    events: list,
) -> dict:
    required = ["event_id", "attendee_id", "ticket_type", "payment_method"]
    for key in required:
        if key not in registration_data:
            raise ValueError(f"Missing required field '{key}' for registration.")

    event = _find_event(events, registration_data["event_id"])

    confirmed = _event_confirmed_registrations(registrations, event["id"])
    capacity = int(event.get("capacity", 0))
    on_waitlist = len(confirmed) >= capacity

    reg_id = registration_data.get("id") or uuid.uuid4().hex[:10]
    existing_ids = {r.get("id") for r in registrations}
    if reg_id in existing_ids:
        raise ValueError(f"Registration id '{reg_id}' already exists.")

    base = {
        "id": reg_id,
        "event_id": event["id"],
        "attendee_id": registration_data["attendee_id"],
        "ticket_type": registration_data["ticket_type"],
        "seat_number": None,
        "confirmation_code": registration_data.get("confirmation_code") or uuid.uuid4().hex[:8].upper(),
        "payment_method": registration_data["payment_method"],
        "payment_status": registration_data.get("payment_status", "pending"),
        "status": "waitlisted" if on_waitlist else "confirmed",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "checkin_timestamp": None,
        "sessions": registration_data.get("sessions", []),
        "waitlist_position": None,
        "price": float(registration_data.get("price", event.get("price", 0.0))),
    }

    if on_waitlist:
        waitlist = _event_waitlist(registrations, event["id"])
        next_pos = 1
        if waitlist:
            next_pos = max(r.get("waitlist_position", 0) for r in waitlist) + 1
        base["waitlist_position"] = next_pos
    else:
        base["seat_number"] = len(confirmed) + 1
        base["payment_status"] = registration_data.get("payment_status", "paid")

    registrations.append(base)
    return base


def promote_waitlist(registrations: list, event_id: str) -> dict | None:
    waitlist = sorted(
        _event_waitlist(registrations, event_id),
        key=lambda r: (r.get("waitlist_position") or 0, r.get("created_at", "")),
    )
    if not waitlist:
        return None

    candidate = waitlist[0]
    confirmed = _event_confirmed_registrations(registrations, event_id)

    candidate["status"] = "confirmed"
    candidate["seat_number"] = len(confirmed) + 1
    candidate["waitlist_position"] = None
    candidate["updated_at"] = _now_iso()

    pos = 1
    for r in waitlist[1:]:
        r["waitlist_position"] = pos
        pos += 1

    return candidate


def cancel_registration(
    registrations: list,
    registration_id: str,
    events: list,
) -> dict:
    for r in registrations:
        if r.get("id") == registration_id:
            if r.get("status") == "cancelled":
                return r

            event = _find_event(events, r["event_id"])
            try:
                start = date.fromisoformat(event["start_date"])
            except Exception:
                start = date.today()

            now = date.today()
            if start - now > timedelta(days=2):
                if r.get("payment_status") == "paid":
                    r["payment_status"] = "refunded"
            else:
                if r.get("payment_status") == "paid":
                    r["payment_status"] = "no_refund"

            r["status"] = "cancelled"
            r["updated_at"] = _now_iso()
            return r

    raise ValueError(f"Registration with id '{registration_id}' not found.")


def transfer_ticket(
    registrations: list,
    registration_id: str,
    new_attendee_id: str,
) -> dict:
    for r in registrations:
        if r.get("id") == registration_id:
            if r.get("status") not in {"confirmed", "checked-in"}:
                raise ValueError("Only confirmed or checked-in tickets can be transferred.")
            r["attendee_id"] = new_attendee_id
            r["updated_at"] = _now_iso()
            return r
    raise ValueError(f"Registration with id '{registration_id}' not found.")


def calculate_event_revenue(registrations: list, event_id: str) -> float:
    total = 0.0
    for r in registrations:
        if r.get("event_id") != event_id:
            continue
        status = r.get("payment_status")
        if status in {"paid", "no_refund"}:
            total += float(r.get("price", 0.0))
    return total
