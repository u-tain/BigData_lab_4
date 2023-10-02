import clickhouse_connect
import os,sys
import pandas as pd
import yaml


def connect2bd():
    with open(os.path.join(os.getcwd(),'secrets','secrets.yml'), 'r') as file:
        yml = yaml.safe_load(file)
    yml = [item.split(' ') for item in yml.split('=')]
    return clickhouse_connect.get_client(host=yml[3][1],
                                         username=yml[2][1], 
                                         password=yml[1][1])


def check_clear_db(client):
    for item in ['BBC_News_Train', 'BBC_News_Test', 'targets_BBC', 'Test_features_BBC', 'Train_features_BBC']:
        delete_query = f'DROP TABLE {item};'
        if client.query(f'EXISTS TABLE {item}').result_rows[0][0] == 1:
            client.query(delete_query)


def upload_data():
    client = connect2bd()
    print(client.query("SELECT * FROM system.metrics WHERE metric LIKE '%Connection'"))
    check_clear_db(client)
    # загружаем в базу данных данные для обучения
    querry1 = 'CREATE TABLE IF NOT EXISTS BBC_News_Train ( `Articled` Int, `Text` String, `Category` String) ENGINE = MergeTree ORDER BY Articled'
    client.query(querry1)
    print(os.path.join(os.getcwd(),'data','BBC News Train.csv'))
    df = pd.read_csv(os.path.join(os.getcwd(),'data','BBC News Train.csv'))
    rows = list(df.itertuples(index=False, name=None))
    insert_querry1 = 'INSERT INTO BBC_News_Train VALUES '+str(rows).replace('[','').replace(']','')
    client.query(insert_querry1)

    # загружаем в базу данных данные для теста
    
    querry2 = 'CREATE TABLE IF NOT EXISTS BBC_News_Test ( `Articled` Int, `Text` String) ENGINE = MergeTree ORDER BY Articled'
    client.query(querry2)
    df = pd.read_csv(os.path.join(os.getcwd(),'data','BBC News Test.csv'))
    rows = list(df.itertuples(index=False, name=None))
    insert_querry2 = 'INSERT INTO BBC_News_Test VALUES ' + str(rows).replace('[','').replace(']','')
    client.query(insert_querry2)


if __name__ == "__main__":
    upload_data()
