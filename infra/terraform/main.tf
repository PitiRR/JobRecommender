terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "docker" {}

# Create a shared network
resource "docker_network" "airflow_net" {
  name = "airflow-network"
}

# PostgreSQL Container
resource "docker_container" "postgres" {
  name  = "postgres"
  image = "postgres:15"
  env = [
    "POSTGRES_USER=airflow",
    "POSTGRES_PASSWORD=airflow",
    "POSTGRES_DB=airflow_metadata"
  ]
  ports {
    internal = 5432
    external = 5432
  }
  networks_advanced {
    name = docker_network.airflow_net.name
  }
  volumes {
    volume_name    = "postgres_data"
    container_path = "/var/lib/postgresql/data"
  }
}

# Airflow Container
resource "docker_container" "airflow" {
  name  = "airflow"
  image = "apache/airflow:slim-latest-python3.9"
  env = [
    "AIRFLOW__CORE__EXECUTOR=LocalExecutor",
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow_metadata"
  ]
  ports {
    internal = 8080
    external = 8080
  }
  networks_advanced {
    name = docker_network.airflow_net.name
  }
  volumes {
    host_path      = "${path.cwd}/dags"
    container_path = "/opt/airflow/dags"
  }
  depends_on = [docker_container.postgres]
}

# Persistent Volume for PostgreSQL
resource "docker_volume" "postgres_data" {
  name = "postgres_data"
}