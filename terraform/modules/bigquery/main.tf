resource "google_bigquery_dataset" "banking_analytics" {
  dataset_id    = "banking_analytics"
  friendly_name = "Banking Analytics"
  location      = var.region
  project       = var.project_id
}

resource "google_bigquery_table" "transactions_stream" {
  dataset_id          = google_bigquery_dataset.banking_analytics.dataset_id
  table_id            = "transactions_stream"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }

  schema = jsonencode([
    { name = "transaction_id",   type = "INTEGER",   mode = "REQUIRED" },
    { name = "reference_id",     type = "STRING",    mode = "REQUIRED" },
    { name = "from_account_id",  type = "INTEGER",   mode = "NULLABLE" },
    { name = "to_account_id",    type = "INTEGER",   mode = "NULLABLE" },
    { name = "bank_id",          type = "INTEGER",   mode = "NULLABLE" },
    { name = "transaction_type", type = "STRING",    mode = "REQUIRED" },
    { name = "amount",           type = "NUMERIC",   mode = "REQUIRED" },
    { name = "currency",         type = "STRING",    mode = "NULLABLE" },
    { name = "status",           type = "STRING",    mode = "REQUIRED" },
    { name = "created_at",       type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

resource "google_bigquery_table" "ledger_analytics" {
  dataset_id          = google_bigquery_dataset.banking_analytics.dataset_id
  table_id            = "ledger_analytics"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }

  schema = jsonencode([
    { name = "ledger_id",       type = "INTEGER",   mode = "REQUIRED" },
    { name = "transaction_id",  type = "INTEGER",   mode = "REQUIRED" },
    { name = "account_id",      type = "INTEGER",   mode = "REQUIRED" },
    { name = "entry_type",      type = "STRING",    mode = "REQUIRED" },
    { name = "amount",          type = "NUMERIC",   mode = "REQUIRED" },
    { name = "running_balance", type = "NUMERIC",   mode = "NULLABLE" },
    { name = "created_at",      type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}
