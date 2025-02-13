FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir snowflake-connector-python

CMD ["python", "snowsql-call.py"]


