# JobRecommender

End-to-end data ETL pipeline that extracts available jobs, and recommends best ones with a recommender System

Status: WIP, do not run

## About

### Scope and impact

JobRecommender is a job aggreggator that extracts postings from online boards using an ETL pipeline, stores the data in Clickhouse data warehouse, where you can perform analytics. Find most fitting and personalized job offers ranked using an ML content-based Recommender System algorithm. 

This project runs on-prem with Docker.

### Deliverables

- Onprem (Docker).
- Batch ingestion (daily) ETL pipeline.
- Dimensional data model in a data warehouse.
- Machine learning model for recommendations.
- Dashboards for insights.
- Tech Stack:
  - Terraform and Docker for infra and deployment,
    - DevOps and DataOps (CI/CD, GX primarily)
  - Python 3,
  - pandas for transformation and cleaning,
    - open source
    - pyspark is overkill; up to 100 rows in-memory at a time
  - Airflow for orchestration,
    - open source
    - familiarity over Dagster
  - Clickhouse for Data Warehouse,
    - open source
    - dev-friendly
    - great integration for ml
  - dbt for downstream in-place transformations,
    - for data marts and further modifications
  - Numpy, Scikit-learn, Tensorflow for ML
  - Apache Superset.

## Getting Started

To run this project locally in Docker, follow these steps:

1. `git clone https://github.com/PitiRR/JobRecommender`

1. `cd JobRecommender/infra/terraform`

1. `terraform init`

1. `terraform plan`

1. `terraform apply`

1. Run `localhost:9000` in your browser

## Usage

## Notes

This project is for non-commercial use.

Thanks to Grupa Pracuj (pracuj.pl) for access to resources that help understand allowed and respectful usage of their site, ie. TOS and robots.txt.

# Stuff for me

- Deploying Clickhouse on a local Docker deployment 
  - https://medium.com/@kjdeluna/lets-learn-clickhouse-part-2-setting-up-your-local-clickhouse-cluster-using-docker-75b972f4117f
- Deploying postgres on Docker 
  - https://www.youtube.com/watch?v=Hs9Fh1fr5s8
- Build Docker image locally and deploy container using Terraform 
  - https://agnieszkapasieka.medium.com/build-docker-image-locally-and-deploy-container-using-terraform-6306334fdf0a
