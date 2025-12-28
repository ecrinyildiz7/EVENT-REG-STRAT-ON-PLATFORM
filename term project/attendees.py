from __future__ import annotations

import json
import os
import uuid
from typing import List, Dict, Any, Optional


def load_attendees(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_attendees(path: str, attendees: list) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(attendees, f, indent=2, ensure_ascii=False)


def _generate_pin() -> str:
    import random
    return f"{random.randint(0, 9999):04d}"


def register_attendee(attendees: list, profile: dict) -> dict:
    required = ["name", "email"]
    for key in required:
        if key not in profile or not str(profile[key]).strip():
            raise ValueError(f"Missing required field '{key}' for attendee.")

    email = profile["email"].strip().lower()
    for a in attendees:
        if a.get("email", "").strip().lower() == email:
            raise ValueError("An attendee with this email already exists.")

    aid = profile.get("id") or uuid.uuid4().hex[:8]
    pin = profile.get("pin") or _generate_pin()

    attendee = {
        "id": aid,
        "name": profile["name"].strip(),
        "email": email,
        "organization": profile.get("organization", "").strip(),
        "dietary": profile.get("dietary", "").strip(),
        "ticket_type": profile.get("ticket_type", "General"),
        "pin": pin,
        "communication": profile.get("communication", {"email_opt_in": True}),
    }
    attendees.append(attendee)
    return attendee


def authenticate_attendee(attendees: list, email: str, pin: str) -> dict | None:
    email = email.strip().lower()
    for a in attendees:
        if a.get("email", "").strip().lower() == email and a.get("pin") == pin:
            return a
    return None


def update_attendee(attendees: list, attendee_id: str, updates: dict) -> dict:
    for a in attendees:
        if a.get("id") == attendee_id:
            if "email" in updates:
                new_email = updates["email"].strip().lower()
                for other in attendees:
                    if other is a:
                        continue
                    if other.get("email", "").strip().lower() == new_email:
                        raise ValueError("Another attendee already uses this email.")
                updates["email"] = new_email
            updates.pop("id", None)
            updates.pop("pin", None)

            a.update(updates)
            return a
    raise ValueError(f"Attendee with id '{attendee_id}' not found.")
