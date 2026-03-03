🚀 Cloud-Native Event-Driven Transaction Processing System (GCP)
👨‍💻 Author

Ramesh K R
Senior Cloud Engineer | Python Backend Developer
8+ Years Backend Experience | GCP Cloud-Native Specialist

📌 Project Purpose

This project demonstrates the design and implementation of a cloud-native, event-driven transaction processing system on Google Cloud Platform (GCP).

It simulates secure banking-style fund transfers using:

Transactional integrity

Double-entry ledger design

Asynchronous event-driven processing

Analytics streaming pipeline

IAM-secured cloud architecture

This project is built to showcase architectural thinking, cloud-native engineering, and distributed system design.

🏗 High-Level Architecture
🌐 Frontend Layer

HTML / CSS3 / Bootstrap

JavaScript (Fetch API)

Hosted on VM (Nginx)

HTTPS secured

⚙ Backend Layer

Python (FastAPI)

Stateless containerized service

Deployed on Cloud Run

JWT-based authentication

Structured logging

🗄 Data Layer

Cloud SQL (MySQL)

Row-level locking

ACID transactions

Double-entry ledger model

🔄 Event Layer

Pub/Sub (asynchronous messaging)

Subscriber Cloud Run service

Decoupled notification processing

📊 Analytics Layer

Dataflow (stream processing)

BigQuery (analytics warehouse)

🔐 Security Layer

IAM (Least privilege)

Service accounts

Secret Manager

VPC connector (private DB access)

🔄 Detailed Request & Data Flow
1️⃣ User Initiates Transfer

User clicks “Transfer” on HTML frontend.

JavaScript sends HTTPS request to Cloud Run API.

JWT validated.

FastAPI starts database transaction.

Accounts locked using:

SELECT ... FOR UPDATE


Balance validated.

Transaction record inserted.

Double-entry ledger entries created:

Debit sender

Credit receiver

Commit DB transaction.

Publish event to Pub/Sub.

API returns success response.

2️⃣ Asynchronous Processing

Pub/Sub receives transaction event.

Subscriber service processes event.

Sends email/SMS notification (simulated).

Event streamed via Dataflow to BigQuery.

BigQuery stores analytics data.

Cloud Logging captures structured logs.

Logs archived to Cloud Storage.

🧾 Core Engineering Highlights
🔐 Transaction Safety

ACID-compliant database operations

Row-level locking

Idempotency key handling

Double-entry ledger enforcement

Consistency validation

🔄 Event-Driven Architecture

Core processing isolated from notification pipeline

Pub/Sub decoupling

Retry-safe event publishing

Horizontal scalability

📊 Analytics Isolation

Operational DB (OLTP) and analytics (OLAP) separated:

Cloud SQL → Transactions

BigQuery → Reporting

Dataflow → Streaming pipeline

Prevents performance degradation of core system.

📈 Scalability Design

Cloud Run auto-scaling

Stateless containers

Asynchronous processing

Independent subscriber scaling

🔐 Security Implementation

Secrets stored in Secret Manager

IAM least-privilege service accounts

JWT-based authentication

HTTPS-only communication

No credentials in source code

🛠 CI/CD Pipeline

Automated using Cloud Build:

GitHub push triggers Cloud Build.

Docker image built.

Image pushed to Artifact Registry.

Deployed to Cloud Run.

Versioned deployments supported.

📂 Project Structure
banking-platform/
│
├── app/                # Core FastAPI service
├── subscriber/         # Event consumer service
├── cicd/               # Cloud Build configs
├── Dockerfile
├── requirements.txt
└── README.md

🧠 Design Considerations

Cloud Run selected for serverless scalability.

Pub/Sub ensures decoupled and resilient architecture.

Dataflow used for streaming analytics pipeline.

Double-entry ledger ensures accounting integrity.

Idempotency prevents duplicate transfers.

Structured logging improves observability.

📌 Why This Project Reflects Production Thinking

This architecture incorporates principles used in real cloud-native systems:

Event-driven processing

Database transaction integrity

IAM-based access control

Observability & monitoring

Scalability & cost optimization

Separation of concerns (OLTP vs OLAP)

🔮 Future Enhancements

Fraud detection engine

Redis caching

Distributed tracing

Rate limiting middleware

Multi-region deployment

Chaos testing
