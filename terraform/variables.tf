# DB related
variable "db_username" {
  type    = string
  default = "postgres"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_port" {
  type    = number
  default = 5432
}

# Airflow related
variable "airflow_username" {
  type    = string
  default = "airflow"
}

variable "airflow_password" {
  type      = string
  sensitive = true
}

variable "airflow_web_port" {
  type    = number
  default = 8080
}

variable "airflow_email" {
  type      = string
  sensitive = true
}

# Miscellaneous
variable "rapidapi_key" {
  type      = string
  sensitive = true
}

variable "rapidapi_host" {
  type      = string
  sensitive = true
}

variable "github_token" {
  type      = string
  sensitive = true
}
