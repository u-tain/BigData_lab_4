# Отчет
Ссылка на github репозиторий: https://github.com/u-tain/BigData_lab_4


1. Сделан форк репозитория на GitHub
2. в docker-compose.yml добавлены контейнеры zookeeper, kafka, kafka-consumer, kafka-topics-generator, настроена их работа
3. в predict.py добалена отправка результата модели с помощью kafka-producer
4. Произведена интеграция Kafka сервиса с сервисом хранилища секретов.
5. Исправлен  CI/CD пайплайн:
```
name: ci
on:
  push:
    branches:
      - "main"
jobs:     
  build:
    runs-on: ubuntu-latest  
    env:
       user: ${{ secrets.DB_USER }}
       pass: ${{ secrets.DB_PASS }}
       name_db: ${{ secrets.DB_NAME }}
       ip_db: ${{ secrets.DB_IP }}
       ip_net: ${{ secrets.NET_IP }}
       ip_kafka:  ${{ secrets.KAFKA_IP }}
       port_kafka:  ${{ secrets.KAFKA_PORT }}
       app_ip: ${{ secrets.APP_IP }}
       topics_ip: ${{ secrets.TOP_IP }}
       consumer_ip: ${{ secrets.CON_IP }}
       zookeeper_ip: ${{ secrets.ZOO_IP }}
    steps:
      -
        name: Checkout
        uses: actions/checkout@v3.1.0
      - 
        name: create file with password
        env:
         MY_VAL: ${{ secrets.ANSIBLE_PASS}}
        run: |
          import os
          data = open("secrets/.vault_pass", "w")
          for q in (os.getenv("MY_VAL")):
            data.write(q)
        shell: python
      -
        name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_PASS }}
      -
        name: Build docker
        shell: bash
        run: docker-compose build
      -
        name: Start docker
        shell: bash
        run: docker-compose up -d 
      -
        name: stop app
        shell: bash
        run: docker-compose stop app 
      -
        name: Run docker
        shell: bash
        run: docker-compose run app 
      - 
        name: Stop docker
        shell: bash
        run: docker-compose down
```
результат:
![image](https://github.com/u-tain/BigData_lab_4/assets/43996253/abdf91c5-5fb9-4f56-af0a-aa8c93058b0e)

