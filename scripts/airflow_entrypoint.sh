#!/bin/bash

pip install -r /opt/airflow/requirements.txt

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
