from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncpg
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from channels.gmail_handler import GmailHandler
from channels.whatsapp_handler import WhatsAppHandler
from channels.web_form_handler import router as web_form_router

app = FastAPI(
    title="Customer Success FTE API",
    description="24/7 AI-powered customer support across Email, WhatsApp, and Web",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(web_form_router)
gmail_handler = GmailHandler()
whatsapp_handler = WhatsAppHandler()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }

@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
        messages = await gmail_handler.process_notification(body)
        print(f"[GMAIL] Received {len(messages)} messages")
        return {"status": "processed", "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()
    message = await whatsapp_handler.process_webhook(dict(form_data))
    print(f"[WHATSAPP] Message from {message.get('customer_phone')}: {message.get('content')}")
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )

@app.post("/webhooks/whatsapp/status")
async def whatsapp_status(request: Request):
    form_data = await request.form()
    print(f"[WHATSAPP STATUS] {dict(form_data)}")
    return {"status": "received"}

@app.get("/metrics/channels")
async def get_channel_metrics():
    try:
        DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER','postgres')}:{os.getenv('POSTGRES_PASSWORD','yourpassword')}@{os.getenv('POSTGRES_HOST','localhost')}/{os.getenv('POSTGRES_DB','fte_db')}"
        conn = await asyncpg.connect(DATABASE_URL)
        metrics = await conn.fetch("""
            SELECT initial_channel as channel,
                   COUNT(*) as total_conversations,
                   COUNT(*) FILTER (WHERE status = 'escalated') as escalations
            FROM conversations
            GROUP BY initial_channel
        """)
        await conn.close()
        return {row['channel']: dict(row) for row in metrics}
    except Exception as e:
        return {"error": str(e), "note": "No data yet"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
