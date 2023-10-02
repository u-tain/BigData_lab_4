import os
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
import configparser
import logging
from bd_utils import connect2bd
import traceback
import time



class Model():
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, filename="train.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
        self.config = configparser.ConfigParser()
        self.config.read("src/config.ini")
        self.prodject_path  = os.getcwd().replace('\\','/')

        # подключаемся к базе данных
        self.client = connect2bd()

        query1= self.client.query(f"SELECT * FROM {self.config['READY_DATA_TRAIN']['x_train']}")
        print(query1)
        print(query1.summary)
        time.sleep(1)
        query2= self.client.query(f"SELECT * FROM {self.config['READY_DATA_TRAIN']['y_train']}")
        df1  = pd.DataFrame(columns= np.arange(int(self.config['READY_DATA_TRAIN']['x_train_columns'])),)
        df2 = pd.DataFrame(columns = ['Category'])
        rows1 = query1.result_rows
        rows2 = query2.result_rows
        print(len(rows1))
        print(len(rows2))
        print(len(df1))
        print(len(df2))
        for i in range(len(rows2)):
            df1.loc[len(df1)] = rows1[i]
            df2.loc[len(df2)] = rows2[i]

        self.X_train = [df1.iloc[i, :].array for i in range(len(df1))]
        self.y_train = df2.Category

        self.log_reg_path = os.path.join( self.prodject_path,'experiments', "logreg.sav")
        self.client.close()


    def log_reg(self) -> bool:
        classifier = LogisticRegression(penalty='l2', C=1.0, max_iter=100, random_state=0)
        logging.info('the model has been initialized')
        try:
            print(len(self.X_train))
            classifier.fit(self.X_train, self.y_train)
            classifier_dtb = classifier.predict(self.X_train)
        except Exception:
            traceback.print_exc()
            logging.error("Something went wrong in fit model")
        else:
            logging.info('Model successfully trained')
        params = classifier.get_params()
        self.config['LOGREG'] = {'penalty': params['penalty'],
                                 'C': params['C'],
                                 'max_iter': params['max_iter'],
                                 'random_state': params['random_state'],
                                 'model_path': self.log_reg_path
                                 }
        with open('src/config.ini', 'w') as configfile:
            self.config.write(configfile)
        return self.save_model(classifier, self.log_reg_path)

    def save_model(self, classifier, path: str) -> bool:
        pickle.dump(classifier, open(path, "wb"))
        logging.info('model saved')
        return os.path.isfile(path)


if __name__ == "__main__":
    
    multi_model = Model()
    multi_model.log_reg()
