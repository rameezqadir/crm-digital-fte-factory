import json
from datetime import datetime
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

TOPICS = {
    'tickets_incoming': 'fte.tickets.incoming',
    'email_inbound': 'fte.channels.email.inbound',
    'whatsapp_inbound': 'fte.channels.whatsapp.inbound',
    'webform_inbound': 'fte.channels.webform.inbound',
    'email_outbound': 'fte.channels.email.outbound',
    'whatsapp_outbound': 'fte.channels.whatsapp.outbound',
    'escalations': 'fte.escalations',
    'metrics': 'fte.metrics',
    'dlq': 'fte.dlq'
}

class FTEKafkaProducer:
    """Mock Kafka producer - works without a running Kafka broker."""
    def __init__(self):
        self.messages = []

    async def start(self):
        print("[KAFKA MOCK] Producer started (mock mode - no broker needed)")

    async def stop(self):
        print("[KAFKA MOCK] Producer stopped")

    async def publish(self, topic: str, event: dict):
        event["timestamp"] = datetime.utcnow().isoformat()
        self.messages.append({"topic": topic, "event": event})
        print(f"[KAFKA MOCK] Published to {topic}: {str(event)[:100]}")


class FTEKafkaConsumer:
    """Mock Kafka consumer - works without a running Kafka broker."""
    def __init__(self, topics: list, group_id: str):
        self.topics = topics
        self.group_id = group_id
        print(f"[KAFKA MOCK] Consumer created for topics: {topics}")

    async def start(self):
        print(f"[KAFKA MOCK] Consumer started (mock mode)")

    async def stop(self):
        print(f"[KAFKA MOCK] Consumer stopped")

    async def consume(self, handler):
        print("[KAFKA MOCK] Listening for messages (mock - no real messages will arrive)")
        # In mock mode, just keep alive
        import asyncio
        while True:
            await asyncio.sleep(60)
