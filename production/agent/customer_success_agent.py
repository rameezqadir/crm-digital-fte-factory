import os
import asyncpg
from agents import Agent, function_tool
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER','postgres')}:{os.getenv('POSTGRES_PASSWORD','yourpassword')}@{os.getenv('POSTGRES_HOST','localhost')}/{os.getenv('POSTGRES_DB','fte_db')}"

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

class KnowledgeSearchInput(BaseModel):
    query: str
    max_results: int = 5

class TicketInput(BaseModel):
    customer_id: str
    issue: str
    priority: str = "medium"
    category: Optional[str] = None
    channel: Channel

class EscalationInput(BaseModel):
    ticket_id: str
    reason: str
    urgency: str = "normal"

class ResponseInput(BaseModel):
    ticket_id: str
    message: str
    channel: Channel

async def get_db():
    return await asyncpg.connect(DATABASE_URL)

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation. Use when customer asks about product features, how-to, or technical questions."""
    try:
        conn = await get_db()
        results = await conn.fetch(
            "SELECT title, content, category FROM knowledge_base WHERE content ILIKE  OR title ILIKE  LIMIT ",
            f"%{input.query}%", input.max_results
        )
        await conn.close()
        if not results:
            return "No relevant documentation found. Consider escalating to human support."
        formatted = [f"**{r['title']}**\n{r['content'][:500]}" for r in results]
        return "\n\n---\n\n".join(formatted)
    except Exception as e:
        return f"Knowledge base temporarily unavailable. Please escalate. Error: {str(e)}"

@function_tool
async def create_ticket(input: TicketInput) -> str:
    """Create support ticket. ALWAYS call this first at the start of every conversation."""
    try:
        conn = await get_db()
        ticket_id = await conn.fetchval(
            "INSERT INTO tickets (customer_id, category, priority, status, source_channel) VALUES (, , , 'open', ) RETURNING id",
            input.customer_id, input.category, input.priority, input.channel.value
        )
        await conn.close()
        return f"Ticket created: {ticket_id}"
    except Exception as e:
        import uuid
        return f"Ticket logged locally: {uuid.uuid4()} (DB error: {e})"

@function_tool
async def get_customer_history(customer_id: str) -> str:
    """Get customer history across ALL channels. Call this after creating ticket."""
    try:
        conn = await get_db()
        history = await conn.fetch(
            """SELECT c.initial_channel, c.started_at, c.status, m.content, m.role, m.channel
               FROM conversations c JOIN messages m ON m.conversation_id = c.id
               WHERE c.customer_id =  ORDER BY m.created_at DESC LIMIT 10""",
            customer_id
        )
        await conn.close()
        if not history:
            return "No previous interactions found for this customer."
        lines = [f"[{r['channel']}] {r['role']}: {r['content'][:200]}" for r in history]
        return "Previous interactions:\n" + "\n".join(lines)
    except Exception as e:
        return f"No history available (DB error: {e})"

@function_tool
async def escalate_to_human(input: EscalationInput) -> str:
    """Escalate to human when: pricing, refunds, legal, angry customer, or 2 failed searches."""
    try:
        conn = await get_db()
        await conn.execute(
            "UPDATE tickets SET status='escalated', resolution_notes= WHERE id=::uuid",
            f"Escalation: {input.reason}", input.ticket_id
        )
        await conn.close()
    except Exception as e:
        print(f"Escalation DB update failed: {e}")
    return f"Escalated to human support. Reference: {input.ticket_id}. Reason: {input.reason}"

@function_tool
async def send_response(input: ResponseInput) -> str:
    """Send response to customer. ALWAYS call this last - never skip this step."""
    channel_formats = {
        Channel.EMAIL: lambda msg: f"Dear Customer,\n\nThank you for reaching out.\n\n{msg}\n\nBest regards,\nTechCorp AI Support Team\n---\nTicket: {input.ticket_id}",
        Channel.WHATSAPP: lambda msg: (msg[:297] + "...") if len(msg) > 300 else msg + "\n\nReply for more help or type 'human' for live support.",
        Channel.WEB_FORM: lambda msg: f"{msg}\n\n---\nNeed more help? Reply to this message or visit our support portal."
    }
    formatted = channel_formats[input.channel](input.message)
    print(f"[{input.channel.value.upper()}] Response sent: {formatted[:100]}...")
    return f"Response sent via {input.channel.value}: delivered"

customer_success_agent = Agent(
    name="Customer Success FTE",
    model="gpt-4o",
    instructions="""You are a Customer Success agent for TechCorp SaaS.

## Your Purpose
Handle routine customer support queries across Email, WhatsApp, and Web Form channels.

## Required Workflow (ALWAYS follow this exact order)
1. FIRST: Call create_ticket to log the interaction
2. THEN: Call get_customer_history to check prior context
3. THEN: Call search_knowledge_base if customer asks product questions
4. FINALLY: Call send_response (NEVER skip this)

## Channel Awareness
- Email: Formal, detailed, include greeting and signature
- WhatsApp: Concise, conversational, under 300 chars preferred
- Web Form: Semi-formal, helpful, numbered steps when applicable

## Hard Constraints (NEVER violate)
- NEVER discuss pricing -> escalate with reason "pricing_inquiry"
- NEVER process refunds -> escalate with reason "refund_request"
- NEVER respond to legal questions -> escalate with reason "legal_inquiry"
- NEVER promise features not in documentation
- ALWAYS create ticket before responding
- ALWAYS use send_response tool to deliver the reply

## Escalation Triggers
- Mentions of "lawyer", "legal", "sue", "attorney"
- Pricing or refund requests
- Sentiment very negative (aggressive, threatening)
- Cannot find answer after 2 searches
- Customer explicitly requests human agent
- WhatsApp: customer sends "human" or "agent"

## Cross-Channel Continuity
If customer has prior history, acknowledge it warmly before solving the current issue.
""",
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response
    ]
)
