# EVENT-REG-STRAT-ON-PLATFORM
Overview

The purpose of this project is to provide a lightweight, offline platform for conference or event organizers.
Users can:
•	Create and manage events and sessions
•	Register attendees and update their profiles
•	Process ticket purchases and waitlists
•	Check in attendees and generate badges
•	View event attendance and revenue statistics
•	All data is saved locally using JSON, so the system works without internet access.

Technologies Used:
•	Python (Standard library only)
•	JSON for persistence
•	File-based backups and login
•	No external packages are required.

Features
Category	Features
Events	Create & update events, add sessions/workshops
Attendees	Register and authenticate attendees using email + PIN
Registration	Ticketing, seat assignment, payment records, waitlist handling
Check-In	Confirm attendance and generate text badges
Reports	Attendance, revenue, and session popularity summaries

Project Structure
main.py
events.py
attendees.py
registration.py
checkin.py
storage.py
reports.py
data/
backups/
badges/


data/ stores JSON files for events, attendees, and registrations
backups/ contains timestamped backups
badges/ stores generated attendance badges
Folders are automatically created when needed.

How to Run
1.	Make sure Python 3.9+ is installed
2.	Open a terminal inside the project folder
3.	Run:

python main.py
1.	Then follow the on-screen menu.

2.	Usage Roles
2.1.	The system includes three menus:
2.2.	Organizer: manage events, attendees, ticketing, reports
2.3.	Staff: check-in on event day, track attendance
2.4.	Attendee: create profile, log in, register for events, print badge
3.	Each action is immediately saved.

4.	Example Workflow
4.1.	Organizer creates a new event
4.2.	Attendees register using email + PIN
4.3.	Organizer registers attendees into the event
4.4.	System assigns seats or places on waitlist
4.5.	On event day, staff check in participants
4.6.	Badge files are generated in /badges/ folder
4.7.	Organizer views attendance + revenue reports
4.8.	Testing
4.9.	Includes basic automated tests checking:
4.10.	Capacity enforcemen
4.11.	Waitlist promotion
4.12.	Check-in behavior
4.13.	Run tests with:
4.14.	python -m pytest


