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
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=postgres"
  ]
  ports {
    internal = 5432
    external = 5432
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
  image = "apache/airflow:latest-python3.9"
  env = [
    "AIRFLOW__CORE__EXECUTOR=LocalExecutor",
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgresql:5432/airflow_db"
  ]
  ports {
    internal = 8080
    external = 8080
  }
  networks_advanced {
    name = docker_network.airflow_net.name
  }


  volumes {
      host_path      = abspath("${path.cwd}/../dags")
      container_path = "/opt/airflow/dags"
    }
    volumes {
      host_path      = abspath("${path.cwd}/../src")
      container_path = "/opt/airflow/plugins/src"
    }
    volumes {
      host_path      = abspath("${path.cwd}/../requirements.txt")
      container_path = "/opt/airflow/requirements.txt"
    }  
    volumes {
      host_path      = abspath("${path.cwd}/../scripts/airflow_entrypoint.sh")
      container_path = "/entrypoint.sh"
    }
    volumes {
      host_path      = abspath("${path.cwd}/../logs")
      container_path = "/opt/airflow/plugins/logs"
    }
    volumes {
      host_path      = abspath("${path.cwd}/../.env")
      container_path = "/opt/airflow/plugins/.env"
    }

    command = ["bash", "-c", "chmod +x /entrypoint.sh && /entrypoint.sh"]

    depends_on = [docker_container.postgresql]
}
