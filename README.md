# JobRecommender

End-to-end data ETL pipeline that extracts available jobs, and recommends best-fitting ones with a recommender System

Status: WIP

## About

### Scope and impact

JobRecommender is a job aggreggator that extracts postings from online boards using an ETL pipeline, stores the data in Clickhouse data warehouse, where you can perform analytics. Find most fitting and personalized job offers ranked using an ML content-based Recommender System algorithm. 

This project runs on-prem with Docker.

### Deliverables

- Onprem (Docker).
- Batch ingestion (daily) ETL pipeline.
- Database to retain historical data.
- Machine learning model for recommendations.
- Dashboards for insights.
- Tech Stack:
  - Terraform and Docker for infra and deployment,
  - Python 3.9,
  - pandas for transformation and cleaning,
  - Airflow for orchestration,
  - Postgresql for data storage,
  - dbt for downstream in-place transformations,
  - Numpy, Scikit-learn, Tensorflow for ML
  - Apache Superset.

## Getting Started

To run this project locally in Docker, follow these steps:

1. `git clone https://github.com/PitiRR/JobRecommender`

1. `cd JobRecommender/terraform`

1. `docker build -t airflow-selenium:latest ../`
   - Building via Terraform returns 'unexpected EOF' error.

1. `terraform init`

1. `terraform plan`

1. `terraform apply`

1. Run `localhost:8080` in your browser

## Usage

## Notes

### Dockerfile

I think Airflow + Selenium is a useful deployment combination. I tried to parameterize it to a reasonable way and I hope whoever reads this finds it useful, as I wasn't satisfied with what I found on the web.

Since Selenium 4.11, you don't need to download the browser driver or even the browser! However, you still need the dependencies. Not something you'd even think about if running in your workstation CLI, but essential to have - containers don't come with those. `scripts/chrome_dependencies.sh` sorts this out.

Selenium should store the browser/browserdriver binaries in `/home/airflow/.cache/selenium/...`. You can find required dependencies by running `ldd chrome`, for example.

Finally, unlike official docker-compose, airflow image doesn't create the user or run webserver out of the box. You need to do it yourself.

### Areas to explore

- Data Warehouse for additional analytics, bi or downstream use. 
  - Clickhouse seems good.

### Other

This project is for non-commercial use.

Thanks to Grupa Pracuj (pracuj.pl) for access to resources that help understand allowed and respectful usage of their site, ie. TOS and robots.txt.
