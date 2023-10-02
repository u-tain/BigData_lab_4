import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import configparser
import logging
from bd_utils import connect2bd
import numpy as np


class DataPreprocess():
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, filename="preprocess.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
        # подключаемся к базе данных
        self.client = connect2bd()
        self.x_table_name = 'Train_features_BBC'
        self.y_table_name = 'targets_BBC'
        self.x_test_table_name = 'Test_features_BBC'

        self.config = configparser.ConfigParser()
        self.config['DATA'] = {'train': 'BBC_News_Train',
                               'test': 'BBC_News_Test'}

    def get_data(self) -> bool:
        # записываем запрос обучающих данных в датафрейм
        query = self.client.query("SELECT Text, Category FROM BBC_News_Train")
        dataset = pd.DataFrame(query.result_rows,columns=['Text','Category'])

        self.X = pd.DataFrame(dataset.Text)
        self.y = pd.DataFrame(dataset.Category)

        # записываем запрос тестовых данных в датафрейм
        query = self.client.query("SELECT * FROM BBC_News_Test")
        dataset = pd.DataFrame(query.result_rows,columns=['idx','Text'])
        self.X_test = pd.DataFrame(dataset.Text)
        

    def prepare_labels(self, targets):
        self.labels_to_id = {key: i for i, key in enumerate(targets.Category.unique())}
        self.id_to_labels = dict(zip(self.labels_to_id.values(), self.labels_to_id.keys()))
        targets.Category = targets.Category.apply(lambda x: self.labels_to_id[x])
        return targets.Category

    def prepare_text(self, features, mode: str):
        if mode == 'train':
            self.tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2),
                                         stop_words='english')
            features = self.tfidf.fit_transform(features.Text).toarray()
        else:
            features = self.tfidf.transform(features.Text.tolist()).toarray()
        return features

    def prepare_data(self) -> bool:
        try:
            self.get_data()
        except:
            logging.error("Error in get data")
            return False
        else:
            logging.info("Data received")

        X = self.prepare_text(self.X, mode='train')
        y = self.prepare_labels(self.y)
        X_test = self.prepare_text(self.X_test, mode='test')
        logging.info("Data ready")

        self.config['READY_DATA_TRAIN'] = {'X_train': self.x_table_name,
                                           'y_train': self.y_table_name}
        self.config['READY_DATA_TEST'] = {'X_test': self.x_test_table_name}

        self.config['READY_DATA_TRAIN']['x_train_columns'] = str(self.save_ready_data(X, self.x_table_name, 'Text'))
        self.config['READY_DATA_TRAIN']['y_train_columns'] = str(self.save_ready_data(y, self.y_table_name, 'Category'))
        self.config['READY_DATA_TEST']['x_test_columns'] = str(self.save_ready_data(X_test, self.x_test_table_name, 'Text'))
        logging.info('Data saved')
        
        with open('src/config.ini', 'w') as configfile:
            self.config.write(configfile)
        self.client.close()
        

    def save_ready_data(self, arr, name: str, mode: str) -> bool:
        #TODO: проверить если таблица существует, то удалить и создать заново
        items = arr.tolist()
        df = pd.DataFrame()
        if mode == 'Text':
            df = pd.DataFrame(arr.tolist())
        else:
            df[mode] = items
        df = df.reset_index(drop=True)
        print(len(df))
        # создаем таблицу для результата обработки данных

        if 'Range' in str(df.columns):
            columns = np.arange(df.columns.start,df.columns.stop)
        else: 
            columns = df.columns
        num_columns = len(columns)
        columns = [f'`{item}` FLOAT' for item in columns]
        columns = str(columns).replace('[','').replace(']','').replace("'","")
        print(name)
        text_query = f'CREATE TABLE  IF NOT EXISTS {name}  ({columns}) ENGINE = MergeTree ORDER BY tuple()'
        delete_query = f'DROP TABLE {name};'
        if self.client.query(f'EXISTS TABLE {name}').result_rows[0][0] == 1:
            print('delete')
            self.client.query(delete_query)
        self.client.query(text_query)
        print(len(df))
        batch_size = 6
        for i in range(batch_size):
            if i!=batch_size-1:
                rows = df.iloc[(len(df)//batch_size)*i:(i+1)*(len(df)//batch_size)].values.tolist() 
            else: 
                rows = df.iloc[(len(df)//batch_size)*i:].values.tolist() 
            rows = str(rows)[1:-1].replace('[','(').replace(']',')').replace('\n','')
            insert_query = f'INSERT INTO {name}  VALUES {rows} '
            self.client.query(insert_query )
        return num_columns


if __name__ == "__main__":
    import time
    start = time.time()
    data_preprocess = DataPreprocess()
    data_preprocess.prepare_data()
    print(time.time()-start)
