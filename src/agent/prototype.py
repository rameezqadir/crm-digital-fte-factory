import os
import json
from anthropic import Anthropic
from datetime import datetime

client = Anthropic()
conversation_history = []
tickets = []

def load_docs():
    with open('../context/product-docs.md', 'r') as f:
        return f.read()

def load_escalation_rules():
    with open('../context/escalation-rules.md', 'r') as f:
        return f.read()

PRODUCT_DOCS = load_docs()
ESCALATION_RULES = load_escalation_rules()

SYSTEM_PROMPT = f"""You are a Customer Success agent for TechCorp SaaS.

PRODUCT KNOWLEDGE:
{PRODUCT_DOCS}

ESCALATION RULES:
{ESCALATION_RULES}

CHANNEL BEHAVIOR:
- email: Formal, use Dear/Best regards, detailed responses (max 500 words)
- whatsapp: Casual, short (<300 chars preferred), end with 'Reply for more or type human'  
- web_form: Semi-formal, helpful, include steps when needed (max 300 words)

ALWAYS:
1. Create a ticket for every interaction
2. Check if escalation is needed before responding
3. Adapt tone and length to the channel
4. NEVER discuss pricing, refunds, or legal matters - escalate those

Respond in JSON format:
{{
  "ticket_id": "T-<timestamp>",
  "channel": "<channel>",
  "response": "<your response to customer>",
  "escalate": true/false,
  "escalation_reason": "<reason if escalating>",
  "sentiment": "positive/neutral/negative",
  "topic": "<main topic>"
}}
"""

def process_message(customer_message: str, channel: str, customer_id: str) -> dict:
    ticket_id = f"T-{int(datetime.now().timestamp())}"
    
    conversation_history.append({
        "role": "user",
        "content": f"[Channel: {channel}] [Customer: {customer_id}] Message: {customer_message}"
    })
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )
    
    response_text = response.content[0].text
    
    try:
        result = json.loads(response_text)
    except:
        result = {
            "ticket_id": ticket_id,
            "channel": channel,
            "response": response_text,
            "escalate": False,
            "sentiment": "neutral",
            "topic": "general"
        }
    
    result["ticket_id"] = ticket_id
    tickets.append({
        "id": ticket_id,
        "customer_id": customer_id,
        "channel": channel,
        "message": customer_message,
        "response": result.get("response"),
        "escalated": result.get("escalate", False),
        "timestamp": datetime.now().isoformat()
    })
    
    conversation_history.append({
        "role": "assistant",
        "content": response_text
    })
    
    return result

def format_response(result: dict) -> str:
    print(f"\n{'='*50}")
    print(f"Ticket ID: {result.get('ticket_id')}")
    print(f"Channel: {result.get('channel')}")
    print(f"Sentiment: {result.get('sentiment')}")
    print(f"Escalate: {result.get('escalate')}")
    if result.get('escalation_reason'):
        print(f"Escalation Reason: {result.get('escalation_reason')}")
    print(f"\nAgent Response:\n{result.get('response')}")
    print('='*50)
    return result.get('response', '')

def run_demo():
    test_cases = [
        {"msg": "I forgot my password, how do I reset it?", "channel": "whatsapp", "id": "customer_001"},
        {"msg": "Dear Support, I am having trouble with the Slack integration. It stopped working 2 days ago.", "channel": "email", "id": "customer_002"},
        {"msg": "How much does the enterprise plan cost?", "channel": "web_form", "id": "customer_003"},
        {"msg": "YOUR APP IS BROKEN AND I HAVE A MEETING IN 10 MINUTES", "channel": "whatsapp", "id": "customer_004"},
        {"msg": "I need to talk to your legal department about our contract", "channel": "email", "id": "customer_005"},
    ]
    
    print("CRM Digital FTE - Prototype Demo")
    print("="*50)
    
    for test in test_cases:
        print(f"\nINBOUND [{test['channel'].upper()}]: {test['msg']}")
        result = process_message(test['msg'], test['channel'], test['id'])
        format_response(result)
    
    print(f"\n\nTotal tickets created: {len(tickets)}")
    escalated = [t for t in tickets if t['escalated']]
    print(f"Escalated: {len(escalated)}")

if __name__ == "__main__":
    run_demo()
