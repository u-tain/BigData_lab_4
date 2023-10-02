import unittest
import os
import sys 
sys.path.insert(1, os.path.join(os.getcwd(), "src"))
from predict import Predictor


class TestPredictor(unittest.TestCase):
    def setUp(self) -> None:
        self.predictor = Predictor()

    def test_predict(self):
        self.assertEqual(self.predictor.predict(), True)

    def test_postproc(self):
        example = [0, 1, 1, 2, 3, 4, 1, 2, 0]
        self.assertEqual(len(self.predictor.post_process(example)), len(example))
    def runTest(self):
        self.test_predict()
        self.test_postproc()
        
