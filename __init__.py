"""Учебная методика фиксации метрик интерфейсных сценариев IDE."""
from .model import Observation, ProtocolError
from .report import build_report, paired_differences
from .storage import read_observations, write_observation

__all__ = ['Observation', 'ProtocolError', 'build_report', 'paired_differences', 'read_observations', 'write_observation']
