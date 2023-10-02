from bd_utils import *
from preprocess import *
from train import *
from predict import *
from unit_tests.test_preprocess import *
from unit_tests.test_train import *
from unit_tests.test_predict import *
import time



if __name__ == "__main__":
    # time.sleep(1)
    upload_data()
    print('loaded')
    DataPreprocess().prepare_data()
    print('preprocessed')
    trainer = Model()
    trainer.log_reg()
    print('trained')
    predicted = Predictor()
    predicted.predict()
    print('predicted')
    # запускаем тесты
    TestDataPreprocess()()
    TestTrain()()
    TestPredictor()()
