FROM apache/airflow:latest-python3.9

USER root

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    chromium \
    chromium-driver

COPY requirements.txt .
COPY scripts/airflow_entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow

RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /opt/airflow

ENTRYPOINT ["/entrypoint.sh"]