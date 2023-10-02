import unittest
import sys
import os
sys.path.insert(1, os.path.join(os.getcwd(), "src"))
from train import Model


class TestTrain(unittest.TestCase):
    def setUp(self) -> None:
        self.trainer = Model()

    def test_log_reg(self):
        self.assertEqual(self.trainer.log_reg(), True)
    
    def runTest(self):
        self.test_log_reg()
