from __future__ import annotations

import csv
import json
import os
from typing import List, Dict, Any


def attendance_report(events: list, registrations: list) -> dict:
    report: dict[str, dict] = {}

    for e in events:
        eid = e.get("id")
        capacity = int(e.get("capacity", 0))
        registered = len([r for r in registrations if r.get("event_id") == eid and r.get("status") != "cancelled"])
        checked_in = len([r for r in registrations if r.get("event_id") == eid and r.get("status") == "checked-in"])

        report[eid] = {
            "event_name": e.get("name"),
            "capacity": capacity,
            "registered": registered,
            "checked_in": checked_in,
            "remaining": max(capacity - registered, 0),
        }

    return report


def revenue_report(events: list, registrations: list) -> dict:
    per_event: dict[str, dict] = {}

    for e in events:
        per_event[e["id"]] = {
            "event_name": e.get("name"),
            "revenue": 0.0,
        }

    for r in registrations:
        eid = r.get("event_id")
        if eid not in per_event:
            continue
        if r.get("payment_status") in {"paid", "no_refund"}:
            per_event[eid]["revenue"] += float(r.get("price", 0.0))

    return per_event


def session_popularity(events: list, registrations: list) -> dict:
    result: dict[str, dict] = {}
    session_titles: dict[tuple[str, str], str] = {}
    for e in events:
        eid = e.get("id")
        for s in e.get("sessions", []):
            session_titles[(eid, s["id"])] = s.get("title", s["id"])

    for e in events:
        eid = e["id"]
        result[eid] = {}

    for r in registrations:
        eid = r.get("event_id")
        if eid not in result:
            continue
        sessions = r.get("sessions", [])
        for sid in sessions:
            key = (eid, sid)
            title = session_titles.get(key, sid)
            stats = result[eid].setdefault(
                sid,
                {"session_title": title, "registered": 0, "checked_in": 0},
            )
            if r.get("status") in {"confirmed", "checked-in"}:
                stats["registered"] += 1
            if r.get("status") == "checked-in":
                stats["checked_in"] += 1

    return result


def export_report(report: dict, filename: str) -> str:
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    if filename.lower().endswith(".json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    elif filename.lower().endswith(".csv"):
        keys = set()
        for _, item in report.items():
            if isinstance(item, dict):
                keys.update(item.keys())
        keys = sorted(keys)
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["key"] + keys)
            for rid, item in report.items():
                row = [rid]
                for k in keys:
                    row.append(item.get(k, "") if isinstance(item, dict) else "")
                writer.writerow(row)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2, ensure_ascii=False))

    return filename
