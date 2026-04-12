# Operations Runbook - CRM Digital FTE

## Service URLs
- API: http://localhost:8000 (local) / https://support-api.yourdomain.com (prod)
- Health: GET /health
- Web Form: http://localhost:3000 (local)
- Metrics: GET /metrics/channels

## Starting the Stack (Local Development)

### Option 1: Docker Compose (Recommended)
docker-compose up -d

### Option 2: Manual
1. Start PostgreSQL: docker start fte-postgres
2. Start Kafka: docker start fte-kafka
3. Start API: python production/api/main.py
4. Start Web Form: cd web-form && npm run dev

## Common Issues & Fixes

### API not starting
- Check .env file has all required variables
- Verify PostgreSQL is running: docker ps | grep postgres
- Check logs: docker logs fte-postgres

### Database connection errors
- Verify POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD in .env
- Test connection: psql -h localhost -U postgres -d fte_db

### Kafka connection errors
- Verify Kafka is running: docker ps | grep kafka
- Check KAFKA_BOOTSTRAP_SERVERS in .env

### WhatsApp not receiving messages
- Verify Twilio webhook URL points to your public URL
- Use ngrok for local testing: ngrok http 8000
- Set webhook in Twilio console to https://your-ngrok-url/webhooks/whatsapp

### Gmail not receiving messages
- Verify Gmail API credentials in credentials.json
- Re-run OAuth flow if credentials expired

## Kubernetes Commands
kubectl get pods -n customer-success-fte
kubectl logs -f deployment/fte-api -n customer-success-fte
kubectl scale deployment fte-api --replicas=5 -n customer-success-fte
kubectl describe pod <pod-name> -n customer-success-fte

## Monitoring
- Check channel metrics: GET /metrics/channels
- Check Kubernetes HPA: kubectl get hpa -n customer-success-fte
- View recent tickets in PostgreSQL:
  SELECT * FROM tickets ORDER BY created_at DESC LIMIT 10;

## Emergency Escalation
If agent is not responding: 
1. Check /health endpoint
2. Restart pod: kubectl rollout restart deployment/fte-api -n customer-success-fte
3. Manually assign tickets to human agents via tickets table
   UPDATE tickets SET status='manual_review' WHERE status='open' AND created_at < NOW() - INTERVAL '10 minutes';
