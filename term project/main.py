from __future__ import annotations

import os
from typing import List, Dict, Any

import events
import attendees as attendees_mod
import registration as reg_mod
import checkin as checkin_mod
import storage
import reports as reports_mod


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _print_events(events_list: list) -> None:
    if not events_list:
        print("No events.")
        return
    print("{:<8} {:<25} {:<10} {:<10} {:<8} {:<8}".format("ID", "Name", "Start", "End", "Cap", "Price"))
    print("-" * 80)
    for e in events_list:
        print(
            "{:<8} {:<25} {:<10} {:<10} {:<8} {:<8}".format(
                e.get("id", "")[:8],
                e.get("name", "")[:25],
                e.get("start_date", ""),
                e.get("end_date", ""),
                e.get("capacity", ""),
                e.get("price", ""),
            )
        )


def _print_registrations(registrations_list: list) -> None:
    if not registrations_list:
        print("No registrations.")
        return
    print("{:<10} {:<8} {:<8} {:<10} {:<10} {:<10}".format("Reg ID", "Event", "Att", "Status", "Pay", "Seat"))
    print("-" * 80)
    for r in registrations_list:
        print(
            "{:<10} {:<8} {:<8} {:<10} {:<10} {:<10}".format(
                r.get("id", "")[:10],
                r.get("event_id", "")[:8],
                r.get("attendee_id", "")[:8],
                r.get("status", ""),
                r.get("payment_status", ""),
                str(r.get("seat_number", "")),
            )
        )


def _print_attendees(attendees_list: list) -> None:
    if not attendees_list:
        print("No attendees.")
        return
    print("{:<8} {:<25} {:<25} {:<10}".format("ID", "Name", "Email", "Ticket"))
    print("-" * 80)
    for a in attendees_list:
        print(
            "{:<8} {:<25} {:<25} {:<10}".format(
                a.get("id", "")[:8],
                a.get("name", "")[:25],
                a.get("email", "")[:25],
                a.get("ticket_type", ""),
            )
        )


def organizer_menu(events_list: list, attendees_list: list, registrations_list: list) -> None:
    while True:
        print("\n=== Organizer Menu ===")
        print("1) Manage events")
        print("2) Manage attendees")
        print("3) Manage registrations")
        print("4) Reports & analytics")
        print("5) Backup data")
        print("0) Back to role selection")
        choice = input("Choose: ").strip()

        if choice == "1":
            manage_events(events_list)
            storage.save_state(BASE_DIR, events_list, attendees_list, registrations_list)
        elif choice == "2":
            manage_attendees(attendees_list)
            storage.save_state(BASE_DIR, events_list, attendees_list, registrations_list)
        elif choice == "3":
            manage_registrations(events_list, attendees_list, registrations_list)
            storage.save_state(BASE_DIR, events_list, attendees_list, registrations_list)
        elif choice == "4":
            run_reports(events_list, registrations_list)
        elif choice == "5":
            backups_dir = os.path.join(BASE_DIR, "backups")
            paths = storage.backup_state(BASE_DIR, backups_dir)
            print(f"Created {len(paths)} backup files.")
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def manage_events(events_list: list) -> None:
    while True:
        print("\n--- Event Management ---")
        _print_events(events_list)
        print("\n1) Create event")
        print("2) Update event")
        print("3) Add session")
        print("4) List sessions")
        print("0) Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            location = input("Location: ").strip()
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            capacity = input("Capacity: ").strip()
            price = input("Price: ").strip()
            desc = input("Description (optional): ").strip()
            try:
                event = events.create_event(
                    events_list,
                    {
                        "name": name,
                        "location": location,
                        "start_date": start_date,
                        "end_date": end_date,
                        "capacity": capacity,
                        "price": price,
                        "description": desc,
                    },
                )
                print(f"Created event with id {event['id']}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            eid = input("Event ID to update: ").strip()
            updates: dict[str, Any] = {}
            print("Leave blank to keep current value.")
            for e in events_list:
                if e.get("id") == eid:
                    new_name = input(f"Name [{e['name']}]: ").strip()
                    if new_name:
                        updates["name"] = new_name
                    loc = input(f"Location [{e['location']}]: ").strip()
                    if loc:
                        updates["location"] = loc
                    sd = input(f"Start date [{e['start_date']}]: ").strip()
                    if sd:
                        updates["start_date"] = sd
                    ed = input(f"End date [{e['end_date']}]: ").strip()
                    if ed:
                        updates["end_date"] = ed
                    cap = input(f"Capacity [{e['capacity']}]: ").strip()
                    if cap:
                        updates["capacity"] = cap
                    pr = input(f"Price [{e['price']}]: ").strip()
                    if pr:
                        updates["price"] = pr
                    st = input(f"Status [{e.get('status','scheduled')}]: ").strip()
                    if st:
                        updates["status"] = st
                    try:
                        events.update_event(events_list, eid, updates)
                        print("Event updated.")
                    except ValueError as ex:
                        print(f"Error: {ex}")
                    break
            else:
                print("Event not found.")

        elif choice == "3":
            eid = input("Event ID for session: ").strip()
            title = input("Session title: ").strip()
            speaker = input("Speaker: ").strip()
            room = input("Room: ").strip()
            capacity = input("Capacity: ").strip()
            start_time = input("Start (YYYY-MM-DD or datetime; blank for none): ").strip()
            end_time = input("End (YYYY-MM-DD or datetime; blank for none): ").strip()
            sdata = {
                "title": title,
                "speaker": speaker,
                "room": room,
                "capacity": capacity,
            }
            if start_time:
                sdata["start_time"] = start_time
            if end_time:
                sdata["end_time"] = end_time
            try:
                session = events.add_session(events_list, eid, sdata)
                print(f"Added session with id {session['id']}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "4":
            eid = input("Event ID: ").strip()
            try:
                sessions = events.list_sessions(events_list, eid)
                if not sessions:
                    print("No sessions.")
                else:
                    print("{:<8} {:<25} {:<15} {:<10}".format("ID", "Title", "Speaker", "Cap"))
                    print("-" * 70)
                    for s in sessions:
                        print(
                            "{:<8} {:<25} {:<15} {:<10}".format(
                                s.get("id", "")[:8],
                                s.get("title", "")[:25],
                                s.get("speaker", "")[:15],
                                s.get("capacity", ""),
                            )
                        )
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def manage_attendees(attendees_list: list) -> None:
    while True:
        print("\n--- Attendee Management ---")
        _print_attendees(attendees_list)
        print("\n1) Register attendee")
        print("2) Update attendee")
        print("0) Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            org = input("Organization: ").strip()
            diet = input("Dietary needs: ").strip()
            ticket_type = input("Ticket type (General/VIP/etc.): ").strip() or "General"
            try:
                attendee = attendees_mod.register_attendee(
                    attendees_list,
                    {
                        "name": name,
                        "email": email,
                        "organization": org,
                        "dietary": diet,
                        "ticket_type": ticket_type,
                    },
                )
                print(f"Registered attendee {attendee['name']} with id {attendee['id']} and pin {attendee['pin']}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            aid = input("Attendee ID: ").strip()
            for a in attendees_list:
                if a.get("id") == aid:
                    print("Leave blank to keep current.")
                    new_name = input(f"Name [{a['name']}]: ").strip()
                    email = input(f"Email [{a['email']}]: ").strip()
                    org = input(f"Organization [{a['organization']}]: ").strip()
                    diet = input(f"Dietary [{a['dietary']}]: ").strip()
                    ticket_type = input(f"Ticket type [{a['ticket_type']}]: ").strip()

                    updates: dict[str, Any] = {}
                    if new_name:
                        updates["name"] = new_name
                    if email:
                        updates["email"] = email
                    if org:
                        updates["organization"] = org
                    if diet:
                        updates["dietary"] = diet
                    if ticket_type:
                        updates["ticket_type"] = ticket_type

                    try:
                        attendees_mod.update_attendee(attendees_list, aid, updates)
                        print("Attendee updated.")
                    except ValueError as e:
                        print(f"Error: {e}")
                    break
            else:
                print("Attendee not found.")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def manage_registrations(events_list: list, attendees_list: list, registrations_list: list) -> None:
    while True:
        print("\n--- Registration Management ---")
        _print_registrations(registrations_list)
        print("\n1) Create registration")
        print("2) Cancel registration")
        print("3) Transfer ticket")
        print("4) Promote waitlist for an event")
        print("0) Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            _print_events(events_list)
            eid = input("Event ID: ").strip()
            _print_attendees(attendees_list)
            aid = input("Attendee ID: ").strip()
            ticket_type = input("Ticket type (General/VIP/etc.): ").strip() or "General"
            payment_method = input("Payment method (Card/Cash/etc.): ").strip() or "Card"
            sessions_raw = input("Session IDs (comma-separated, optional): ").strip()
            sessions = [s.strip() for s in sessions_raw.split(",") if s.strip()]
            price_str = input("Override price? (blank to use event price): ").strip()

            price = None
            if price_str:
                try:
                    price = float(price_str)
                except Exception:
                    print("Invalid price, using event default.")
                    price = None

            reg_data = {
                "event_id": eid,
                "attendee_id": aid,
                "ticket_type": ticket_type,
                "payment_method": payment_method,
                "sessions": sessions,
            }
            if price is not None:
                reg_data["price"] = price

            try:
                reg = reg_mod.create_registration(registrations_list, reg_data, events_list)
                if reg["status"] == "waitlisted":
                    print(
                        f"Event full. Registration waitlisted at position {reg['waitlist_position']} "
                        f"with confirmation {reg['confirmation_code']}."
                    )
                else:
                    print(
                        f"Registration confirmed with id {reg['id']}, seat {reg['seat_number']}, "
                        f"confirmation {reg['confirmation_code']}."
                    )
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            rid = input("Registration ID to cancel: ").strip()
            confirm = input("Are you sure? (y/N): ").strip().lower()
            if confirm == "y":
                try:
                    cancelled = reg_mod.cancel_registration(registrations_list, rid, events_list)
                    print(
                        f"Cancelled registration. Payment status is now {cancelled.get('payment_status')}."
                    )
                    # After cancellation, try promoting waitlist
                    eid = cancelled["event_id"]
                    promoted = reg_mod.promote_waitlist(registrations_list, eid)
                    if promoted:
                        print(
                            f"Waitlisted registration {promoted['id']} has been promoted to confirmed seat "
                            f"{promoted['seat_number']}."
                        )
                except ValueError as e:
                    print(f"Error: {e}")

        elif choice == "3":
            rid = input("Registration ID to transfer: ").strip()
            _print_attendees(attendees_list)
            new_aid = input("New attendee ID: ").strip()
            confirm = input("Confirm transfer? (y/N): ").strip().lower()
            if confirm == "y":
                try:
                    reg_mod.transfer_ticket(registrations_list, rid, new_aid)
                    print("Ticket transferred.")
                except ValueError as e:
                    print(f"Error: {e}")

        elif choice == "4":
            eid = input("Event ID: ").strip()
            promoted = reg_mod.promote_waitlist(registrations_list, eid)
            if promoted:
                print(
                    f"Promoted registration {promoted['id']} to confirmed seat {promoted['seat_number']}."
                )
            else:
                print("No one on waitlist.")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")
            

def run_reports(events_list: list, registrations_list: list) -> None:
    while True:
        print("\n--- Reports & Analytics ---")
        print("1) Attendance report")
        print("2) Revenue report")
        print("3) Session popularity")
        print("4) Export attendance report to JSON")
        print("0) Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            rep = reports_mod.attendance_report(events_list, registrations_list)
            for eid, row in rep.items():
                print(
                    f"{eid}: {row['event_name']} | cap={row['capacity']} "
                    f"reg={row['registered']} checked-in={row['checked_in']} remaining={row['remaining']}"
                )

        elif choice == "2":
            rep = reports_mod.revenue_report(events_list, registrations_list)
            for eid, row in rep.items():
                print(f"{eid}: {row['event_name']} | revenue={row['revenue']}")

        elif choice == "3":
            rep = reports_mod.session_popularity(events_list, registrations_list)
            for eid, sessions in rep.items():
                print(f"Event {eid}:")
                if not sessions:
                    print("  No sessions.")
                for sid, stats in sessions.items():
                    print(
                        f"  {sid}: {stats['session_title']} | reg={stats['registered']} "
                        f"checked-in={stats['checked_in']}"
                    )

        elif choice == "4":
            rep = reports_mod.attendance_report(events_list, registrations_list)
            path = os.path.join(BASE_DIR, "reports", "attendance.json")
            out = reports_mod.export_report(rep, path)
            print(f"Attendance report exported to {out}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")




def staff_menu(events_list: list, attendees_list: list, registrations_list: list) -> None:
    while True:
        print("\n=== Staff Menu ===")
        print("1) Check in by confirmation code or registration ID")
        print("2) List checked-in attendees for event")
        print("3) Session attendance stats")
        print("0) Back to role selection")
        choice = input("Choose: ").strip()

        if choice == "1":
            code = input("Confirmation code or registration ID: ").strip()
            try:
                checked = checkin_mod.check_in_attendee(registrations_list, code)
                print(
                    f"Checked in registration {checked['id']} "
                    f"for attendee {checked['attendee_id']} at {checked['checkin_timestamp']}."
                )
                storage.save_state(BASE_DIR, events_list, attendees_list, registrations_list)
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            _print_events(events_list)
            eid = input("Event ID: ").strip()
            checked = checkin_mod.list_checked_in_attendees(registrations_list, eid)
            print(f"{len(checked)} attendees checked in.")
            for r in checked:
                print(
                    f"Reg {r['id']} | attendee {r['attendee_id']} | seat {r.get('seat_number')} "
                    f"| at {r.get('checkin_timestamp')}"
                )

        elif choice == "3":
            _print_events(events_list)
            eid = input("Event ID: ").strip()
            sid = input("Session ID: ").strip()
            stats = checkin_mod.session_attendance(registrations_list, eid, sid)
            print(
                f"Session {stats['session_id']} | registered={stats['registered']} "
                f"checked-in={stats['checked_in']}"
            )

        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def attendee_menu(events_list: list, attendees_list: list, registrations_list: list) -> None:
    while True:
        print("\n=== Attendee Menu ===")
        print("1) Register as new attendee")
        print("2) Log in (email + pin)")
        print("0) Back to role selection")
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            org = input("Organization: ").strip()
            diet = input("Dietary needs: ").strip()
            ticket_type = input("Preferred ticket type (General/VIP/etc.): ").strip() or "General"
            try:
                attendee = attendees_mod.register_attendee(
                    attendees_list,
                    {
                        "name": name,
                        "email": email,
                        "organization": org,
                        "dietary": diet,
                        "ticket_type": ticket_type,
                    },
                )
                storage.save_state(BASE_DIR, events_list, attendees_list, registrations_list)
                print(
                    f"Welcome {attendee['name']}! Your attendee ID is {attendee['id']} "
                    f"and your PIN for login is {attendee['pin']}."
                )
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            email = input("Email: ").strip()
            pin = input("PIN (4 digits): ").strip()
            user = attendees_mod.authenticate_attendee(attendees_list, email, pin)
            if not user:
                print("Invalid credentials.")
            else:
                attendee_logged_in_menu(user, events_list, registrations_list)
                storage.save_state(BASE_DIR, events_list, attendees_list, registrations_list)

        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def attendee_logged_in_menu(attendee: dict, events_list: list, registrations_list: list) -> None:
    aid = attendee["id"]
    while True:
        print(f"\n--- Attendee: {attendee['name']} ---")
        print("1) View my registrations")
        print("2) Register for an event")
        print("3) Generate my badge for a registration")
        print("0) Log out")
        choice = input("Choose: ").strip()

        my_regs = [r for r in registrations_list if r.get("attendee_id") == aid]

        if choice == "1":
            if not my_regs:
                print("You have no registrations.")
            else:
                for r in my_regs:
                    print(
                        f"Reg {r['id']} | Event {r['event_id']} | status={r['status']} "
                        f"| confirmation={r['confirmation_code']} | payment={r['payment_status']}"
                    )

        elif choice == "2":
            _print_events(events_list)
            eid = input("Event ID to register for: ").strip()
            ticket_type = input(f"Ticket type [{attendee.get('ticket_type','General')}]: ").strip() or attendee.get(
                "ticket_type", "General"
            )
            pay_method = input("Payment method (Card/Cash/etc.): ").strip() or "Card"
            sessions_raw = input("Session IDs (comma-separated, optional): ").strip()
            sessions = [s.strip() for s in sessions_raw.split(",") if s.strip()]

            reg_data = {
                "event_id": eid,
                "attendee_id": aid,
                "ticket_type": ticket_type,
                "payment_method": pay_method,
                "sessions": sessions,
            }
            try:
                reg = reg_mod.create_registration(registrations_list, reg_data, events_list)
                if reg["status"] == "waitlisted":
                    print(
                        f"You are waitlisted at position {reg['waitlist_position']} "
                        f"with confirmation {reg['confirmation_code']}."
                    )
                else:
                    print(
                        f"Registration confirmed! ID {reg['id']}, seat {reg['seat_number']}, "
                        f"confirmation {reg['confirmation_code']}."
                    )
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "3":
            if not my_regs:
                print("You have no registrations.")
                continue
            for r in my_regs:
                print(
                    f"Reg {r['id']} | event {r['event_id']} | status={r['status']} "
                    f"| confirmation={r['confirmation_code']}"
                )
            rid = input("Registration ID to generate badge for: ").strip()
            for r in my_regs:
                if r.get("id") == rid:
                    badges_dir = os.path.join(BASE_DIR, "badges")
                    path = checkin_mod.generate_badge(attendee, r, badges_dir)
                    print(f"Badge generated at {path}")
                    break
            else:
                print("Registration not found.")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")




def main() -> None:
    events_list, attendees_list, registrations_list = storage.load_state(BASE_DIR)

    while True:
        print("\n=== Event Platform ===")
        print("1) Organizer")
        print("2) Staff (check-in)")
        print("3) Attendee")
        print("0) Exit")
        role = input("Choose role: ").strip()

        if role == "1":
            organizer_menu(events_list, attendees_list, registrations_list)
        elif role == "2":
            staff_menu(events_list, attendees_list, registrations_list)
        elif role == "3":
            attendee_menu(events_list, attendees_list, registrations_list)
        elif role == "0":
            # auto-save + backup
            storage.save_state(BASE_DIR, events_list, attendees_list, registrations_list)
            backups_dir = os.path.join(BASE_DIR, "backups")
            storage.backup_state(BASE_DIR, backups_dir)
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
