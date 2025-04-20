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
    "POSTGRES_USER=${var.airflow_username}",
    "POSTGRES_PASSWORD=${var.airflow_password}",
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
  healthcheck {
    test     = ["CMD", "pg_isready", "-U", var.airflow_username]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }
}

# Airflow Container
resource "docker_container" "airflow_webserver" {
  name  = "airflow-webserver"
  image = "airflow-selenium:latest"

  env = [
    "AIRFLOW__CORE__EXECUTOR=LocalExecutor",
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${var.airflow_username}:${var.airflow_password}@postgresql:5432/airflow_db",
    "AIRFLOW__CORE__LOAD_EXAMPLES=False",
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
    container_path = "/opt/airflow/logs"
  }
  # Sometimes you get an error with 'sheduler not running'
  depends_on = [docker_container.postgresql, docker_container.airflow_scheduler]
  command = ["webserver"]
  healthcheck {
    # Values taken from the official docker compose
    test         = ["CMD", "curl", "--fail", "http://localhost:8080/health"]
    interval     = "10s"
    timeout      = "10s"
    retries      = 5
    start_period = "5s"
  }
}

resource "docker_container" "airflow_scheduler" {
  name  = "airflow-scheduler"
  image = "airflow-selenium:latest"

  env = [
    "AIRFLOW__CORE__EXECUTOR=LocalExecutor",
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${var.airflow_username}:${var.airflow_password}@postgresql:5432/airflow_db",
    "AIRFLOW__CORE__LOAD_EXAMPLES=False",
    "RAPIDAPI_KEY=${var.rapidapi_key}",
    "RAPIDAPI_HOST=${var.rapidapi_host}",
    "GITHUB_TOKEN=${var.github_token}",
    "AIRFLOW_EMAIL=${var.airflow_email}",
  ]
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
    container_path = "/opt/airflow/logs"
  }
  depends_on = [docker_container.postgresql]
  command = ["scheduler"]
}
