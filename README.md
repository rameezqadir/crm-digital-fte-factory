# CRM Digital FTE Factory - Hackathon 5

**GitHub**: https://github.com/rameezqadir/crm-digital-fte-factory  
**Author**: rameezqadir

## Overview
A production-grade AI Customer Success FTE (Full-Time Equivalent) that operates 24/7 across three channels: Gmail, WhatsApp, and Web Form.

## Architecture
- **Agent**: OpenAI Agents SDK with GPT-4o
- **API**: FastAPI with channel webhooks
- **Database**: PostgreSQL (serves as CRM)
- **Streaming**: Apache Kafka
- **Deployment**: Kubernetes (minikube)
- **Channels**: Gmail API, Twilio WhatsApp, React/Next.js Web Form

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop
- API keys: OpenAI, Anthropic, Twilio (optional)

### Setup

git clone https://github.com/rameezqadir/crm-digital-fte-factory
cd crm-digital-fte-factory
cp .env.example .env  # Fill in your API keys
docker-compose up -d

### Test

# Health check
curl http://localhost:8000/health

# Submit a web form ticket
curl -X POST http://localhost:8000/support/submit 
  -H "Content-Type: application/json" 
  -d '{"name":"Test","email":"test@example.com","subject":"Help needed","category":"technical","message":"I need help with the API"}'

## Project Structure

crm-digital-fte-factory/
├── context/           # Company dossier files
├── specs/             # FTE specifications and discovery logs
├── src/agent/         # Prototype agent and MCP server
├── production/
│   ├── agent/         # Production OpenAI Agents SDK agent
│   ├── channels/      # Gmail, WhatsApp, Web Form handlers
│   ├── api/           # FastAPI application
│   ├── database/      # PostgreSQL schema
│   ├── k8s/           # Kubernetes manifests
│   └── tests/         # E2E and load tests
├── web-form/          # Next.js support form
├── docs/              # Runbook and documentation
├── docker-compose.yml
└── Dockerfile

## Supported Channels

| Channel | Integration | Response Style |
|---------|------------|----------------|
| Email (Gmail) | Gmail API + Pub/Sub | Formal, detailed |
| WhatsApp | Twilio API | Concise, conversational |
| Web Form | Next.js + FastAPI | Semi-formal |

## Agent Capabilities
- Answers product questions from knowledge base
- Creates and tracks support tickets (PostgreSQL CRM)
- Detects customer sentiment
- Escalates to humans when needed
- Maintains cross-channel conversation history
- Formats responses per channel requirements

## Cost Comparison

| | Human FTE | Digital FTE |
| |---|---|---|
| Annual Cost | ,000+ | <,000 |
| Availability | 8h/day, 5d/week | 24/7/365 |
| Response Time | 4+ hours | <30 seconds |
| Scalability | Hire more people | Auto-scaling |

## Running Tests

cd production
pytest tests/test_e2e.py -v --asyncio-mode=auto
locust -f tests/load_test.py --host=http://localhost:8000
