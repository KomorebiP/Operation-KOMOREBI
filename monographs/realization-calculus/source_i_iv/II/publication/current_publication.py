"""Read current source-bound publication inputs without changing formal evidence."""
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'publication/PUBLICATION_BUILD_CONFIG.json'
ACCEPTED = 'kernel_checked_semantically_accepted_scope'
PARTIAL = 'kernel_checked_partial_scope_open_bridge'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def configuration(map_path=None, edition_date=None):
    config = json.loads(CONFIG.read_text())
    selected = Path(map_path) if map_path is not None else Path(config['correspondence'])
    selected = selected.resolve() if selected.is_absolute() else (ROOT / selected).resolve()
    if not selected.is_relative_to(ROOT):
        raise ValueError('Place the correspondence inside the package before building publication')
    day = date.fromisoformat(edition_date or config['edition_date'])
    return selected, day


def display_date(day):
    return f'{day.day} {day:%B %Y}'


def source_epoch(day):
    return str(int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp()))


def load_scope(path):
    data = json.loads(Path(path).read_text())
    if data.get('schema') not in {'paper-ii-current-correspondence/1', 'paper-ii-current-correspondence/2'}:
        raise ValueError('Unsupported correspondence schema')
    for relative, expected in data['current_chapter_sha256'].items():
        source = ROOT / relative
        if not source.is_file() or sha(source) != expected:
            raise ValueError('Stale current correspondence source: ' + relative)
    rows = [row for row in data['records'] if row['proof_level']]
    counts = dict(Counter(row.get('status', row.get('working_status', 'unclassified')) for row in rows))
    recorded = data.get('final_proof_counts', data.get('working_proof_counts', {}))
    if counts != {key: value for key, value in recorded.items() if value}:
        raise ValueError('Recorded proof counts disagree with the individual source records')
    if len(rows) != data['proof_level_count'] or len(data['records']) != data['record_count']:
        raise ValueError('Recorded source inventory disagrees with the individual source records')
    return data, counts


def scope_summary(data, counts):
    accepted = counts.get(ACCEPTED, 0)
    partial = counts.get(PARTIAL, 0)
    total = data['proof_level_count']
    summary = (f'{accepted} of {total} proof-level source records have kernel checked, '
               'semantically accepted scope. ')
    if partial:
        summary += f'{partial} records retain kernel checked partial scope. '
    other = total - accepted - partial
    if other:
        summary += f'{other} records retain the construction or review states listed in the correspondence. '
    if accepted == total:
        summary += 'No partial or pending proof records are listed in this correspondence. '
    if data.get('known_open_bridge_labels'):
        summary += 'The named open bridges remain explicit in that record. '
    summary += 'These are source-record counts under their stated hypotheses, not counts of independent discoveries.'
    return summary
