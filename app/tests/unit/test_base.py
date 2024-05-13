import os
import unittest

from unittest.mock import MagicMock

class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Start before all test')
        if not os.path.exists("./tests/unit/logs"):
            os.mkdir("./tests/unit/logs")


    @classmethod
    def tearDownClass(cls):
        print('Start after all test')


    def setUp(self):    
        self.logs = open(f"./tests/unit/logs/{self._testMethodName}.log", mode='w', encoding="utf-8")

    def tearDown(self):
        self.logs.close()

if __name__ == '__main__':
    unittest.main()