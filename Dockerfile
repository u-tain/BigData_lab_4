FROM python:3.10

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
ENTRYPOINT ["/bin/sh", "-c" , "cat secrets/.vault_pass && chmod 600 secrets/.vault_pass && ansible-playbook secrets/ansible_playbook.yml --vault-password-file secrets/.vault_pass && python src/main.py && ls && cd secrets && ls && rm -f secrets.yml"]
