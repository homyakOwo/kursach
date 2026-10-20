import tempfile
import unittest
from pathlib import Path
from ide_study import Observation, ProtocolError, build_report, paired_differences, read_observations, write_observation
from ide_study.model import TASK_CODES


def obs(participant='P01', task='NAV-01', mode='classic', seconds=12., errors=0, completed=True, ease=3, date='2026-10-20'):
    return Observation(participant,task,mode,seconds,errors,completed,ease,date)


class ObservationTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(obs().task, 'NAV-01')
    def test_four_tasks(self): self.assertEqual(len(TASK_CODES), 4)
    def test_bad_participant(self):
        with self.assertRaises(ProtocolError): obs(participant='')
    def test_bad_task(self):
        with self.assertRaises(ProtocolError): obs(task='XXX')
    def test_bad_mode(self):
        with self.assertRaises(ProtocolError): obs(mode='wrong')
    def test_low_seconds(self):
        with self.assertRaises(ProtocolError): obs(seconds=0)
    def test_high_seconds(self):
        with self.assertRaises(ProtocolError): obs(seconds=8000)
    def test_bad_errors(self):
        with self.assertRaises(ProtocolError): obs(errors=-2)
    def test_bad_ease(self):
        with self.assertRaises(ProtocolError): obs(ease=6)
    def test_bad_date(self):
        with self.assertRaises(ProtocolError): obs(date='tomorrow')


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'data'/'study.csv'
    def tearDown(self): self.tmp.cleanup()
    def test_missing(self): self.assertEqual(read_observations(self.path), [])
    def test_one_roundtrip(self):
        write_observation(self.path, obs())
        self.assertEqual(read_observations(self.path), [obs()])
    def test_two_roundtrip(self):
        write_observation(self.path, obs())
        write_observation(self.path, obs(participant='P02'))
        self.assertEqual(len(read_observations(self.path)), 2)
    def test_invalid_header(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('wrong,headers\n1,2\n', encoding='utf-8')
        with self.assertRaises(ProtocolError): read_observations(self.path)
    def test_invalid_line(self):
        write_observation(self.path, obs())
        with self.path.open('a', encoding='utf-8') as f: f.write('P02,NAV-01,modern,bad,0,1,5,2026-10-20\n')
        with self.assertRaises(ProtocolError): read_observations(self.path)


class ReportTests(unittest.TestCase):
    def test_empty(self): self.assertEqual(build_report([]), [])
    def test_median(self):
        v=build_report([obs(seconds=10),obs(participant='P02',seconds=20)])
        self.assertEqual(v[0]['median_seconds'],15)
    def test_failed_excluded_from_time(self):
        rows=build_report([obs(seconds=10),obs(participant='P02',seconds=100,completed=False)])
        self.assertEqual(rows[0]['median_seconds'], 10)
        self.assertEqual(rows[0]['success_rate'], 50)
    def test_nobody_succeeded(self):
        self.assertIsNone(build_report([obs(completed=False)])[0]['median_seconds'])
    def test_pair(self):
        v=paired_differences([obs(seconds=20),obs(mode='modern',seconds=12)])
        self.assertEqual(v[0]['saved_seconds'],8)
    def test_no_pair_failed(self):
        self.assertEqual(paired_differences([obs(),obs(mode='modern',completed=False)]),[])
    def test_duplicate_pair_ignored(self):
        self.assertEqual(paired_differences([obs(),obs(),obs(mode='modern')]),[])


if __name__ == '__main__': unittest.main()
