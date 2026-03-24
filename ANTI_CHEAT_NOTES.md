# RankRush Anti-Cheat Notes

Current monitoring features:

- fullscreen-required exam entry
- tab switch and blur warnings
- structured violation logging
- fast-submit flagging
- active session lock with heartbeat
- one-question-at-a-time exam flow
- client-side autosave per active exam token
- faculty pages for results, violation logs, and active sessions

Required migrations:

```powershell
python manage.py migrate
```

Faculty pages:

- `Results`: completed attempts, risk labels, reset/testing action, detail view
- `Violation Logs`: warning and fast-submit history
- `Active Sessions`: active, stale, and completed session states

Testing notes:

- use `Reset Attempt` from faculty results to reopen a finished test
- if the student page reports an inactive session, reopen the exam from `View Exams`
- stale sessions are marked automatically from heartbeat inactivity
