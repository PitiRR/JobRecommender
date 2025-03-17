variable "postgres_volume" {
  default = "postgres_data"
}

variable "db_username" {
  default = "postgres"
}

variable "db_password" {
  default = "postgres"
  sensitive = true
}