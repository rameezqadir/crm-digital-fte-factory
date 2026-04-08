# Operations Runbook - CRM Digital FTE Factory
## GitHub: https://github.com/rameezqadir/crm-digital-fte-factory

## Quick Start
1. git clone https://github.com/rameezqadir/crm-digital-fte-factory
2. Copy .env.example to .env and fill in API keys
3. docker-compose up -d
4. Visit http://localhost:8000/health

## Architecture
- FastAPI backend: port 8000
- Next.js web form: port 3000
- PostgreSQL: port 5432
- Kafka: port 9092
- Kubernetes: minikube

## Channel Webhooks
- Gmail: POST /webhooks/gmail
- WhatsApp: POST /webhooks/whatsapp
- Web Form: POST /support/submit
