FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . /app

CMD ["/bin/bash", "./scripts/api/run_prod_bash.sh"] 
