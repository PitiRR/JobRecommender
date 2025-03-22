terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "docker" {}

# Airflow network
resource "docker_network" "airflow_net" {
  name = "airflow-network"
}

# Airflow metadata db
resource "docker_container" "postgresql" {
  name  = "postgresql"
  image = "postgres:15"
  env = [
    "POSTGRES_USER=${var.db_username}",
    "POSTGRES_PASSWORD=${var.db_password}",
  ]
  ports {
    internal = var.db_port
    external = var.db_port
  }
  networks_advanced {
    name = docker_network.airflow_net.name
  }
  volumes {
    host_path      = abspath("${path.cwd}/../scripts/init_db.sql")
    container_path = "/docker-entrypoint-initdb.d/init_db.sql"
  }
}

# Airflow Container
resource "docker_container" "airflow" {
  name  = "airflow"
  image = "airflow-selenium:latest"

  env = [
    "AIRFLOW__CORE__EXECUTOR=LocalExecutor",
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${var.airflow_username}:${var.airflow_password}@postgresql:5432/airflow_db",
    "RAPIDAPI_KEY=${var.rapidapi_key}",
    "RAPIDAPI_HOST=${var.rapidapi_host}",
    "GITHUB_TOKEN=${var.github_token}",
    "AIRFLOW_EMAIL=${var.airflow_email}",
  ]
  ports {
    internal = var.airflow_web_port
    external = var.airflow_web_port
  }
  networks_advanced {
    name = docker_network.airflow_net.name
  }
  volumes {
    host_path      = abspath("${path.cwd}/../src")
    container_path = "/opt/airflow/plugins/src"
  }
  volumes {
    host_path      = abspath("${path.cwd}/../dags")
    container_path = "/opt/airflow/dags"
  }
  volumes {
    host_path      = abspath("${path.cwd}/../logs")
    container_path = "/opt/airflow/plugins/logs"
  }
  depends_on = [docker_container.postgresql]
  command = ["webserver"]
}
