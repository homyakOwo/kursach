"""CSV-хранилище: открытый формат для проверки и пересчёта результатов."""
from __future__ import annotations
import csv
from dataclasses import asdict
from pathlib import Path
from .model import Observation, ProtocolError

FIELDS = ('participant','task','mode','seconds','errors','completed','ease','date')


def write_observation(path: str | Path, observation: Observation) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    write_header = not dest.exists() or dest.stat().st_size == 0
    with dest.open('a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        row = asdict(observation)
        row['completed'] = '1' if observation.completed else '0'
        writer.writerow(row)


def read_observations(path: str | Path) -> list[Observation]:
    source = Path(path)
    if not source.exists():
        return []
    with source.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or tuple(reader.fieldnames) != FIELDS:
            raise ProtocolError('У CSV-файла неверные колонки')
        output = []
        for number, row in enumerate(reader, 2):
            try:
                if row['completed'] not in ('0','1'):
                    raise ProtocolError('Некорректный признак завершения')
                output.append(Observation(
                    participant=row['participant'], task=row['task'], mode=row['mode'],
                    seconds=float(row['seconds']), errors=int(row['errors']),
                    completed=row['completed'] == '1', ease=int(row['ease']), date=row['date']))
            except (ValueError, TypeError, ProtocolError) as exc:
                raise ProtocolError(f'Некорректная строка CSV {number}: {exc}') from exc
        return output
