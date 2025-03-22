#!/bin/bash

echo "Waiting for PostgreSQL..."
while ! nc -z postgresql 5432; do sleep 1; done

airflow db init
airflow users create \
    --username airflow \
    --password airflow \
    --firstname airflow \
    --lastname airflow \
    --role Admin \
    --email m421rifle@gmail.com

airflow scheduler &
airflow webserver
