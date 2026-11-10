# calendar-scripts-example

Example **scripts** (handlers) for the calendar/trainer backend — the ones the
backend runs through a `handle()` entry point.

The library they use lives in
[`calendar-api-client`](https://github.com/lolvalolee/calendar-api-client).
Scripts here contain no API code of their own: they import a model and call it.

## Install the library

```bash
pip install git+https://github.com/lolvalolee/calendar-api-client.git
```

For development against a local copy:

```bash
pip install -e /home/alexander/projects/scripts
```

## A script in one snippet

```python
from calendar_scripts import get_handler_extra_data
from calendar_scripts.models import Message, NotificationTransport

def handle():
    params = get_handler_extra_data()   # {} when the backend passes nothing
    Message.simple_message(
        f"params: {params}",
        NotificationTransport.desktop(),
    )
```

The backend sets `base_url` and `jwt_token` for a running script, so no client
is ever created by hand.

## Run locally

```bash
export base_url="http://127.0.0.1:8000"
export jwt_token="<access token>"

python my_script.py
```

The token identifies the user the script acts as.

## More

- `AGENTS.md` — how to write scripts here (entry point, what not to do,
  encrypted fields, checklist).
- Library docs: `AGENTS.md` and `API.md` in
  [`calendar-api-client`](https://github.com/lolvalolee/calendar-api-client).
