import pandas as pd
import numpy as np
import pickle
import os
import configparser
import logging
from bd_utils import connect2bd

class Predictor():
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, filename="predict.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
        self.config = configparser.ConfigParser()
        self.config.read("src/config.ini")
        self.prodject_path = self.project_path = os.getcwd().replace('\\','/')
        self.client = connect2bd()

        query= self.client.query(f"SELECT * FROM {self.config['READY_DATA_TEST']['X_test']}")
        print(query.summary)
        df  = pd.DataFrame(columns= np.arange(int(self.config['READY_DATA_TEST']['x_test_columns'])),)
        for item in query.result_rows:
            df.loc[len(df)] = item

        self.X_test = [df.iloc[i, :].array for i in range(len(df))]
        self.model_path = self.config['LOGREG']['model_path']
        query = self.client.query(f"SELECT * FROM {self.config['DATA']['test']}")
        self.test_df_before_prepoc  = pd.DataFrame(query.result_rows,columns=['ArticleId','Text'])
        query = self.client.query(f"SELECT * FROM {self.config['DATA']['train']}")
        self.Train = pd.DataFrame(query.result_rows,columns=['idx','Text','Category'])
        del self.Train['idx']

        self.labels_to_id = {key: i for i, key in enumerate(self.Train.Category.unique())}
        self.id_to_labels = dict(zip(self.labels_to_id.values(), self.labels_to_id.keys()))
        self.result_path = os.path.join(self.project_path, 'experiments','result.csv')

    def predict(self) -> bool:
        try:
            classifier = pickle.load(open(self.model_path, "rb"))
        except FileNotFoundError:
            logging.error("Model wasn't trained")
            return False
        logging.info('Start predictions')
        Y_pred = classifier.predict(self.X_test)
        logging.info('Predictions fulfilled')
        Y_pred = self.post_process(Y_pred)
        logging.info('Predictions post-processed')
        print(len(self.test_df_before_prepoc["ArticleId"]))
        print(len(Y_pred))
        results = pd.DataFrame({
            "ArticleId": self.test_df_before_prepoc["ArticleId"],
            "Category": Y_pred[:len(self.test_df_before_prepoc["ArticleId"])]
        })
        self.config['RESULT'] = {'path': self.result_path}
        with open('src/config.ini', 'w') as configfile:
            self.config.write(configfile)
        results.to_csv(self.result_path, index=False)
        logging.info('results written to file ' + self.result_path)
        return True

    def post_process(self, predictions):
        pred_names = []
        for item in predictions:
            pred_names.append(self.id_to_labels[item])
        return pred_names


if __name__ == "__main__":

    predictor = Predictor()
    predictor.predict()
