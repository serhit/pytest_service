import pytest
import time
from common_types import ConfigType, TestResult, FileValidationResult
import glob
import os

import multiprocessing as mp


class ResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == 'call':
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        self.exitcode = exitstatus
        self.passed = len(terminalreporter.stats.get('passed', []))
        self.failed = len(terminalreporter.stats.get('failed', []))
        self.xfailed = len(terminalreporter.stats.get('xfailed', []))
        self.skipped = len(terminalreporter.stats.get('skipped', []))

        self.total_duration = time.time() - terminalreporter._sessionstarttime


class FileRef:
    def __init__(self):
        self.file_name = None

    @pytest.hookimpl
    def pytest_addoption(self, parser):
        parser.addoption("--file", action="store")

    @pytest.hookimpl
    def pytest_configure(self, config):
        self.file_name = config.option.file
        pytest.data_file_name = config.option.file


def _run(file_name: str, file_type: ConfigType, q):
    collector = ResultsCollector()
    file_ref = FileRef()
    plugins = [collector, file_ref]

    _folder = file_type.value
    if os.path.isdir(_folder):
        files = [_folder]
    else:
        _ft = file_type.value.replace('-', '_')
        files = glob.glob(f'test_{_ft}*.py')

    files += ['--file', file_name]

    pytest.main(files, plugins=plugins)

    q.put(collector)


def run_test(file_name: str, file_type: ConfigType):
    # Need to run tests into totally different process to make it not to "stuck" with the first file

    q = mp.Queue()
    p = mp.Process(target=_run, args=(file_name, file_type, q))
    p.start()
    collector = q.get()
    p.join()

    failed_tests = []
    for report in collector.reports:
        if 'failed' in report.outcome:
            props = {r[0]: r[1] for r in report.user_properties}
            tst = TestResult(id=report.nodeid,
                             outcome=report.outcome,
                             rule="".join(report.head_line.split('test_')[-1].split('[')[0]),
                             line_no=props.get('line_no', -1),
                             field_name=str(props.get('field_name', '')),
                             ref=str(props.get('ref', '')))
            failed_tests.append(tst)

    file_res = FileValidationResult(
        file_name=file_name,
        result=collector.exitcode,
        passed_cnt=collector.passed,
        failed_cnt=collector.failed,
        xfailed_cnt=collector.xfailed,
        skipped_cnt=collector.skipped,
        total_duration_sec=collector.total_duration,
        failed_tests=failed_tests
    )

    return file_res
