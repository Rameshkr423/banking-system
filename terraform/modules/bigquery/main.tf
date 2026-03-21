resource "google_bigquery_dataset" "banking_analytics" {
  dataset_id    = "banking_analytics"
  friendly_name = "Banking Analytics"
  location      = var.region
  project       = var.project_id
}

# ── Existing: Transactions Stream ────────────────────────────
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

# ── Existing: Ledger Analytics ────────────────────────────────
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
    { name = "ledger_id",       type = "INTEGER",   mode = "NULLABLE" },
    { name = "transaction_id",  type = "INTEGER",   mode = "REQUIRED" },
    { name = "account_id",      type = "INTEGER",   mode = "REQUIRED" },
    { name = "entry_type",      type = "STRING",    mode = "REQUIRED" },
    { name = "amount",          type = "NUMERIC",   mode = "REQUIRED" },
    { name = "running_balance", type = "NUMERIC",   mode = "NULLABLE" },
    { name = "created_at",      type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

# ── NEW: User Registrations ───────────────────────────────────
resource "google_bigquery_table" "user_registrations" {
  dataset_id          = google_bigquery_dataset.banking_analytics.dataset_id
  table_id            = "user_registrations"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "registered_at"
  }

  schema = jsonencode([
    { name = "user_id",        type = "INTEGER",   mode = "NULLABLE" },
    { name = "full_name",      type = "STRING",    mode = "NULLABLE" },
    { name = "email",          type = "STRING",    mode = "NULLABLE" },
    { name = "phone",          type = "STRING",    mode = "NULLABLE" },
    { name = "account_number", type = "STRING",    mode = "NULLABLE" },
    { name = "bank_name",      type = "STRING",    mode = "NULLABLE" },
    { name = "branch_name",    type = "STRING",    mode = "NULLABLE" },
    { name = "registered_at",  type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

# ── NEW: Fraud Alerts ─────────────────────────────────────────
resource "google_bigquery_table" "fraud_alerts" {
  dataset_id          = google_bigquery_dataset.banking_analytics.dataset_id
  table_id            = "fraud_alerts"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "detected_at"
  }

  schema = jsonencode([
    { name = "transaction_id",   type = "STRING",    mode = "NULLABLE" },
    { name = "account_id",       type = "INTEGER",   mode = "NULLABLE" },
    { name = "amount",           type = "FLOAT64",   mode = "NULLABLE" },
    { name = "transaction_type", type = "STRING",    mode = "NULLABLE" },
    { name = "reason",           type = "STRING",    mode = "NULLABLE" },
    { name = "severity",         type = "STRING",    mode = "NULLABLE" },
    { name = "detected_at",      type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

# ── NEW: Simulation Logs ──────────────────────────────────────
resource "google_bigquery_table" "simulation_logs" {
  dataset_id          = google_bigquery_dataset.banking_analytics.dataset_id
  table_id            = "simulation_logs"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "simulated_at"
  }

  schema = jsonencode([
    { name = "accounts_created",   type = "INTEGER",   mode = "NULLABLE" },
    { name = "transfers_executed", type = "INTEGER",   mode = "NULLABLE" },
    { name = "transfers_skipped",  type = "INTEGER",   mode = "NULLABLE" },
    { name = "initial_deposit",    type = "INTEGER",   mode = "NULLABLE" },
    { name = "simulated_at",       type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}