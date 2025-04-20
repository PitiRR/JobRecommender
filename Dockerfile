FROM apache/airflow:latest-python3.12

USER root

RUN apt-get update && apt-get install -y \
    wget \
    unzip

COPY scripts/chrome_dependencies.sh .
RUN bash chrome_dependencies.sh

COPY requirements.txt .
COPY scripts/airflow_entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow

RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /opt/airflow

ENTRYPOINT ["/entrypoint.sh"]