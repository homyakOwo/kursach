"""Описательные показатели и парные сравнения без статистических обещаний."""
from __future__ import annotations
from collections import defaultdict
from statistics import median
from .model import Observation


def build_report(observations: list[Observation]) -> list[dict]:
    grouped: dict[tuple[str,str],list[Observation]] = defaultdict(list)
    for obs in observations:
        grouped[obs.task,obs.mode].append(obs)
    rows = []
    for (task, mode), group in sorted(grouped.items()):
        successes = [o for o in group if o.completed]
        rows.append({
            'task':task, 'mode':mode,'attempts':len(group),
            'successes':len(successes), 'success_rate':round(100*len(successes)/len(group),1),
            'median_seconds':round(median(o.seconds for o in successes),2) if successes else None,
            'median_errors':round(median(o.errors for o in group),2),
            'median_ease':round(median(o.ease for o in group),2),
        })
    return rows


def paired_differences(observations: list[Observation]) -> list[dict]:
    """Пары считаются только при ровно одной успешной попытке на условие."""
    grouped: dict[tuple[str,str,str],list[Observation]] = defaultdict(list)
    for o in observations:
        if o.completed:
            grouped[o.participant,o.task,o.mode].append(o)
    keys = sorted({(participant, task) for participant,task,_ in grouped})
    pairs = []
    for participant,task in keys:
        old=grouped.get((participant,task,'classic'), [])
        new=grouped.get((participant,task,'modern'), [])
        if len(old) == 1 and len(new) == 1:
            delta=round(old[0].seconds-new[0].seconds,2)
            pairs.append({'participant':participant,'task':task,
                          'classic_seconds':old[0].seconds,
                          'modern_seconds':new[0].seconds,
                          'saved_seconds':delta})
    return pairs
