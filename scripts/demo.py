"""Только ИЛЛЮСТРАТИВНЫЕ данные для проверки расчётов; не эксперимент!"""
from __future__ import annotations
import tempfile
from pathlib import Path
from ide_study import Observation, write_observation, read_observations, build_report, paired_differences


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'illustrative.csv'
        for person,base in [('DEMO01',32),('DEMO02',28)]:
            write_observation(path, Observation(person,'NAV-01','classic',base,1,True,3,'2026-10-20'))
            write_observation(path, Observation(person,'NAV-01','modern',base-5,0,True,4,'2026-10-20'))
        print('ВНИМАНИЕ: демонстрационные синтетические числа, не измерения разработчиков!')
        print('Сводка:',build_report(read_observations(path)))
        print('Пары:',paired_differences(read_observations(path)))


if __name__ == '__main__': main()
