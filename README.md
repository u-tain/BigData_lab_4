# Отчет
Ссылка на github репозиторий: https://github.com/u-tain/BigData_lab_3


1. Сделан форк репозитория на GitHub
2. С помощью cygwin64 был установлен ansible на windows
3. С помощью ansible-vault были закодированы необходимые секреты
4. Написан ansible-playbook, результатом которого является файл с раскодированными секретами. Этот файл удаляется по завершению работы сервиса app
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
        name: Run docker
        shell: bash
        run: docker-compose run app 
      - 
        name: Stop docker
        shell: bash
        run: docker-compose down
```
Результат:

![image](https://github.com/u-tain/BigData_lab_3/assets/43996253/95d1e229-50e9-4181-9c2e-02a14194e180)
