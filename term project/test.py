import os
import tempfile

import events
import registration as reg_mod
import storage


def test_capacity_and_waitlist():
    with tempfile.TemporaryDirectory() as tmp:
        base = tmp
        evts = []
        e = events.create_event(
            evts,
            {
                "name": "TestConf",
                "location": "X",
                "start_date": "2030-01-01",
                "end_date": "2030-01-02",
                "capacity": 1,
                "price": 100.0,
            },
        )
        attendees_list = []
        regs = []
        r1 = reg_mod.create_registration(
            regs,
            {
                "event_id": e["id"],
                "attendee_id": "A1",
                "ticket_type": "General",
                "payment_method": "Card",
            },
            evts,
        )
        assert r1["status"] == "confirmed"
        r2 = reg_mod.create_registration(
            regs,
            {
                "event_id": e["id"],
                "attendee_id": "A2",
                "ticket_type": "General",
                "payment_method": "Card",
            },
            evts,
        )
        assert r2["status"] == "waitlisted"
        reg_mod.cancel_registration(regs, r1["id"], evts)
        promoted = reg_mod.promote_waitlist(regs, e["id"])
        assert promoted is not None
        assert promoted["id"] == r2["id"]
        assert promoted["status"] == "confirmed"
