import unittest
import os

from datadirtest import DataDirTester
from freezegun import freeze_time


class TestComponent(unittest.TestCase):

    @freeze_time("2024-08-12")
    def test_functional_dtypes(self):
        os.environ['KBC_DATA_TYPE_SUPPORT'] = 'authoritative'
        functional_tests = DataDirTester(data_dir='./tests/functional_dtypes')
        functional_tests.run()

    @freeze_time("2023-04-02")
    def test_functional(self):
        os.environ['KBC_STACKID'] = 'connection.keboola.com'
        os.environ['KBC_PROJECT_FEATURE_GATES'] = 'queuev2'
        functional_tests = DataDirTester(data_dir='./tests/functional_legacy')
        functional_tests.run()


if __name__ == "__main__":
    unittest.main()
