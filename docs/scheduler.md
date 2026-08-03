# Scheduled Dorks

The scheduler runs saved dorks on a recurring timer in the background, so you can keep a
set of searches going without babysitting the UI.

## How it works

- The scheduler is a daemon thread started when the main window opens
  (`Scheduler` in `src/lostdock/services/scheduler.py`).
- It polls the repository every 30 seconds for schedules that are **due**.
- When a schedule is due, it runs the linked saved dork through the same query pipeline
  the UI uses (`run_query`), creating a new job and storing its results.
- After a run, `next_run_at` is advanced by the schedule's interval, and the scheduler
  thread returns to polling.

Schedules live in the `schedules` table. Each row references a saved dork by name, stores
the interval in minutes, the engine to use, and the next/last run timestamps.

## Setting up a schedule

1. **Save the dork** — build your query and click **Save** in the toolbar (or name it in
   the "Dork name" field first). The dork must be saved before it can be scheduled.
2. **Open Tools → Settings** — under "Schedule dork", select the saved dork from the
   list.
3. **Set the interval** — minutes between runs.
4. **Save** — the schedule is written to the database and the scheduler picks it up on
   its next poll.

The schedule uses the engine stored on it. The default engine for new schedules is
**DuckDuckGo** — the lightest engine, chosen to keep automated runs from tripping
bot-checks on Google/Bing at scale.

## Behavior details

- **Polling** — the scheduler checks every 30 seconds; a due run starts on the next poll
  rather than at an exact wall-clock time.
- **Missing dorks** — if a scheduled run finds the saved dork has been deleted, the
  orphaned schedule is removed automatically and a warning is logged. To stop a schedule
  cleanly, delete its saved dork (the schedule is cleaned up on the next poll).
- **Error handling** — if a scheduled run fails, the error is surfaced through the
  scheduler's `on_error` callback (shown in the UI) and the schedule keeps its next run.
- **Persistence** — schedules and their results are stored in SQLite, so they survive app
  restarts. Results from scheduled runs appear as regular jobs in the database and can be
  exported or re-checked like any others.
- **Disabling** — delete the saved dork to stop its schedule. The scheduler detects the
  missing dork on its next poll, removes the orphaned schedule, and logs a warning.
  There is no separate "remove schedule" control; deleting the dork is the way to stop it.
