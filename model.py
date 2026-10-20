"""Описание наблюдения без хранения ФИО участников."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import re

class ProtocolError(ValueError):
    """Ошибочные данные измерения."""


TASK_CODES = ('NAV-01', 'NAV-02', 'EDIT-01', 'DIAG-01')
MODES = ('classic', 'modern')


@dataclass(frozen=True)
class Observation:
    participant: str
    task: str
    mode: str
    seconds: float
    errors: int
    completed: bool
    ease: int
    date: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r'[A-Za-z0-9_-]{2,24}', self.participant):
            raise ProtocolError('Код участника: 2-24 символа A-Z, цифры, - или _.')
        if self.task not in TASK_CODES:
            raise ProtocolError(f'Неизвестная задача: {self.task}')
        if self.mode not in MODES:
            raise ProtocolError('Режим должен быть classic или modern')
        if isinstance(self.seconds, bool) or not (0.05 <= float(self.seconds) <= 7200):
            raise ProtocolError('Время должно быть от 0.05 до 7200 секунд')
        if isinstance(self.errors, bool) or not isinstance(self.errors, int) or not 0 <= self.errors <= 99:
            raise ProtocolError('Число ошибок должно быть целым от 0 до 99')
        if not isinstance(self.completed, bool):
            raise ProtocolError('Признак завершения должен быть логическим')
        if isinstance(self.ease, bool) or not isinstance(self.ease, int) or not 1 <= self.ease <= 5:
            raise ProtocolError('Оценка удобства от 1 до 5')
        try:
            date.fromisoformat(self.date)
        except (ValueError, TypeError) as exc:
            raise ProtocolError('Дата в формате ГГГГ-ММ-ДД') from exc
