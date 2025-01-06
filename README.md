# JobRecommender

End-to-end data ETL pipeline that extracts available jobs, and recommends best ones with a recommender System

## About

### Scope

JobRecommender is a project that extracts job postings from online sources using an ETL pipeline, stores them in Clickhouse data warehouse where you can perform analytics and find most fitting job offers ranked based on ML Recommender System algorithm.

This project runs on Docker.

### Deliverables

- Onprem (Docker)
- Data pipeline (ETL).
- Dimensional data model in a data warehouse.
- Machine learning model for recommendations.
- Visualizations for insights.
- Tech Stack:
  - Terraform and Docker for deployment,
    - DevOps and DataOps automation primarly,
  - Python,
  - pandas for transformation and cleaning,
    - open source
    - apache spark is overkill
  - Airflow for orchestration,
    - open sourse
    - familiarity
  - Clickhouse for Data Warehouse,
    - open source
    - dev-friendly
  - dbt for downstream in-place transformations,
    - for data marts and further modifications
  - Apache Superset.

## Getting Started

To run this project locally in Docker, follow these steps:

1. `git clone https://github.com/PitiRR/JobRecommender`

1. `cd JobRecommender`

1. `docker build .`

1. `terraform init`

1. `terraform plan`

1. `terraform apply`

## Usage
