# AGENTS.md — how to write scripts here

**Read this before writing any script in this repository.**

This repo holds **scripts** (handlers) that the calendar/trainer backend runs.
It is **not** the library: the library lives in
[`calendar-api-client`](https://github.com/lolvalolee/calendar-api-client).

---

## 1. What a script is

A script is a module with a single entry point:

```python
def handle():
    ...
```

The backend imports the module and calls `handle()`. That is the whole
contract — no `if __name__ == "__main__"` requirement, no argument parsing.

Parameters come from the server through the `handler_extra_data` environment
variable (JSON):

```python
from calendar_scripts import get_handler_extra_data

def handle():
    params = get_handler_extra_data()   # {} when absent or not valid JSON
    n = params.get("n", 0)
```

`get_handler_extra_data()` never raises — it returns `{}` on a missing
variable or broken JSON.

**Not every value comes from the server.** Before writing `params.get("x")`,
establish where `x` comes from:

- **from the server** — `handler_extra_data` (values typed into a condition or
  a form, or `action.handler_extra_data` of a notification button);
- **a constant** — defined in the script itself (`HABIT_NAME = "..."`).

If it is a constant, use it directly. Do not invent a parameter and do not add
"missing parameter" branches for something the backend never sends.
**When unsure — ask, do not guess.**

---

## 2. Use the library, do not talk to the API yourself

Import a model and call it:

```python
from calendar_scripts.models import Exercise, Message, NotificationTransport

for exercise in Exercise.objects():
    print(exercise.id, exercise.name.value)

Message.simple_message("Hey!", NotificationTransport.desktop())
```

That is a complete, working program. The shared client is created lazily inside
the library from the `base_url` and `jwt_token` environment variables, which
the backend always sets for a running script.

### Do NOT write any of this

```python
# ❌ build a client — the model already knows its resource
client = CalendarClient()
client.exercises.list()

# ❌ internal helper, not for scripts
from calendar_scripts.calendar_client import default_client
default_client().exercises.list()

# ❌ raw HTTP — the library owns the API
import requests
requests.get(f"{base_url}/api/user-exercise/", headers={"Authorization": ...})
```

`CalendarClient` is public, but it is for hosts that manage several accounts
or an explicit token. A script never needs it.

---

## 3. Documentation lives in the library

Two files are the whole contract:

- [`AGENTS.md`](https://github.com/lolvalolee/calendar-api-client/blob/main/AGENTS.md)
  — how to work (models, `PATCH` as a diff, encrypted fields, notifications,
  traps);
- [`API.md`](https://github.com/lolvalolee/calendar-api-client/blob/main/API.md)
  — what exists (models, fields, methods, constants).

**Write code from them alone; do not open the library sources to look
something up.** If a fact you need is missing from both, add it to `API.md` in
the library repo — a documentation gap is a bug, not an excuse to read code.

The library's own internal maintenance rules (`AGENTS-dev.md`) are **not**
relevant here.

---

## 4. Encrypted fields and secrets

Text fields are `{ "value": ..., "keys": [...] }` and are modelled by
`LocalizedValue`. **The library does not encrypt or decrypt** — produce the
pair yourself and send it back unchanged when you do not touch the field.

- Never hardcode tokens, passwords or key passwords in a script.
- Secrets come from the environment (`base_url`, `jwt_token`) or from
  `handler_extra_data` (which the backend controls).
- `extra_data` is **not** encrypted — it is plain user data. Do not put
  secrets in it.

---

## 5. Running a script locally

Set the same environment the backend sets and run the module:

```bash
export base_url="http://127.0.0.1:8000"
export jwt_token="<access token>"

python my_script.py
```

The token is tied to a user — the script acts as that user. To run `handle()`
explicitly, add a temporary call under
`if __name__ == "__main__": handle()` (local testing only).

---

## 6. Layout and naming

- **One script = one `.py` file.** Where it lives does not matter: the root,
  a subdirectory, any nesting — there is no restriction on the location.
- **The file name is the script name** — the backend refers to it, so do not
  rename a file that is already in use without asking.
- No shared helper modules until a concrete need appears: a script the backend
  runs must stay readable on its own.

Examples: `check_habit_not_done_today.py`, `reports/send_weekly_report.py`.

---

## 7. Do not change the library from here

If a script needs a method or filter the library lacks, the change belongs in
[`calendar-api-client`](https://github.com/lolvalolee/calendar-api-client)
(models, resources, client) — not in this repo and not as a workaround inside
the script. Say so and ask before touching the library.

---

## 8. Before you commit a script

1. `handle()` is the entry point and does not require arguments.
2. Every value read from `handler_extra_data` is really sent by the backend —
   otherwise it is a constant.
3. No client is built, no raw HTTP, no `default_client()`.
4. No secrets in the file.
5. The script is readable on its own: no helpful-but-unused abstractions.
