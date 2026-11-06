"""Check that the shared CSV separates announced dates from planning windows."""

import csv
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


schedule = Path(__file__).resolve().parents[1] / 'data' / 'schedule.csv'
with schedule.open(encoding='utf-8', newline='') as source:
    records = list(csv.DictReader(source))

seen = set()
for line, row in enumerate(records, start=2):
    label = f'{schedule.name}:{line}'
    event = row['event'].strip()
    if not event or not row['venue'].strip():
        raise SystemExit(f'{label} needs an event and a venue')
    key = (row['section'], event)
    if key in seen:
        raise SystemExit(f'{label} repeats {event} in the same section')
    seen.add(key)

    event_date = row['event_date']
    window = row['planning_window']
    if row['timing'] == 'announced':
        if not event_date or window or not row['organiser_url']:
            raise SystemExit(f'{label} needs an announced date and source')
        if date.fromisoformat(event_date).isoformat() != event_date:
            raise SystemExit(f'{label} needs a date in YYYY-MM-DD format')
    elif row['timing'] not in {'check date', 'watchlist'} or event_date or not window:
        raise SystemExit(f'{label} needs a planning window and a recognised timing status')

    url = urlsplit(row['organiser_url'])
    if row['organiser_url'] and (url.scheme not in {'http', 'https'} or not url.netloc):
        raise SystemExit(f'{label} has an invalid organiser URL')

if not records:
    raise SystemExit('The schedule has no events')
print(f'Checked {len(records)} schedule rows')
