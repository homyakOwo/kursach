"""Точка входа: python -m ide_study [tasks|timed|report]."""
from __future__ import annotations
import argparse
from datetime import date
from pathlib import Path
from time import perf_counter
from .model import Observation, ProtocolError, MODES, TASK_CODES
from .protocol import TASKS, CONDITIONS
from .report import build_report, paired_differences
from .storage import read_observations, write_observation


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Учебные замеры интерфейсных сценариев IDE')
    p.add_argument('--file', type=Path, default=Path('study_data/observations.csv'), help='CSV для записей')
    sub = p.add_subparsers(dest='action', required=True)
    sub.add_parser('tasks', help='Описания четырёх заданий')
    timer = sub.add_parser('timed', help='Интерактивный замер секунд')
    timer.add_argument('--participant', required=True)
    timer.add_argument('--task', choices=TASK_CODES, required=True)
    timer.add_argument('--mode', choices=MODES, required=True)
    sub.add_parser('report', help='Сводка и парные разницы')
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.action == 'tasks':
        for code, title in TASKS.items():
            print(f'{code}: {title}')
        for code, detail in CONDITIONS.items():
            print(f'{code}: {detail}')
        return 0
    if args.action == 'timed':
        print(f'Задание: {TASKS[args.task]}')
        print(f'Режим: {CONDITIONS[args.mode]}')
        input('Нажмите Enter для начала измерения: ')
        start = perf_counter()
        input('Выполните задачу в IDE и нажмите Enter сразу после завершения: ')
        duration = round(perf_counter()-start, 3)
        completed = input('Результат правильный? [д/н]: ').strip().lower() in ('д','да','y','yes')
        errors = int(input('Сколько ошибок допущено? [0..99]: '))
        ease = int(input('Насколько было удобно? [1..5]: '))
        observation = Observation(args.participant,args.task,args.mode,max(duration,0.05),errors,completed,ease,date.today().isoformat())
        write_observation(args.file, observation)
        print(f'Сохранено: {observation.seconds:.2f} сек., успех={observation.completed}')
        return 0
    rows = read_observations(args.file)
    if not rows:
        print('Измерений пока нет. Это не ошибка.')
        return 0
    for item in build_report(rows):
        print(f"{item['task']:7} {item['mode']:7} n={item['attempts']} "
              f"успех={item['success_rate']}% "
              f"медиана_успешных={item['median_seconds']}с "
              f"ошибки={item['median_errors']} удобство={item['median_ease']}")
    pairs = paired_differences(rows)
    print(f'Сопоставимых пар успешных попыток: {len(pairs)}')
    for pair in pairs:
        print(f"{pair['participant']} {pair['task']}: разница "
              f"classic - modern = {pair['saved_seconds']} с")
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ProtocolError, ValueError) as exc:
        raise SystemExit(f'Ошибка: {exc}') from exc
