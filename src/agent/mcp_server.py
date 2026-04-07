import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from enum import Enum
from datetime import datetime
from typing import Optional

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

# In-memory storage for prototype
tickets_db = {}
customers_db = {}
conversations_db = {}

server = Server("customer-success-fte")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_knowledge_base",
            description="Search product documentation for relevant information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="create_ticket",
            description="Create a support ticket in the system with channel tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "issue": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "channel": {"type": "string", "enum": ["email", "whatsapp", "web_form"]}
                },
                "required": ["customer_id", "issue", "channel"]
            }
        ),
        Tool(
            name="get_customer_history",
            description="Get customer interaction history across ALL channels",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"}
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="escalate_to_human",
            description="Escalate conversation to human support agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "reason": {"type": "string"},
                    "urgency": {"type": "string", "enum": ["low", "normal", "high"]}
                },
                "required": ["ticket_id", "reason"]
            }
        ),
        Tool(
            name="send_response",
            description="Send response to customer via their channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "message": {"type": "string"},
                    "channel": {"type": "string", "enum": ["email", "whatsapp", "web_form"]}
                },
                "required": ["ticket_id", "message", "channel"]
            }
        ),
        Tool(
            name="analyze_sentiment",
            description="Analyze customer message sentiment",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_knowledge_base":
        query = arguments["query"].lower()
        with open("../../context/product-docs.md", "r") as f:
            docs = f.read()
        lines = docs.split('\n')
        relevant = [l for l in lines if any(word in l.lower() for word in query.split())]
        result = '\n'.join(relevant[:10]) if relevant else "No specific documentation found."
        return [TextContent(type="text", text=result)]
    
    elif name == "create_ticket":
        ticket_id = f"TKT-{len(tickets_db)+1:04d}"
        tickets_db[ticket_id] = {
            "id": ticket_id,
            "customer_id": arguments["customer_id"],
            "issue": arguments["issue"],
            "priority": arguments.get("priority", "medium"),
            "channel": arguments["channel"],
            "status": "open",
            "created_at": datetime.now().isoformat()
        }
        return [TextContent(type="text", text=f"Ticket created: {ticket_id}")]
    
    elif name == "get_customer_history":
        cust_id = arguments["customer_id"]
        history = [t for t in tickets_db.values() if t["customer_id"] == cust_id]
        if not history:
            return [TextContent(type="text", text="No previous interactions found.")]
        summary = json.dumps(history[-5:], indent=2)
        return [TextContent(type="text", text=f"Recent history:\n{summary}")]
    
    elif name == "escalate_to_human":
        ticket_id = arguments["ticket_id"]
        if ticket_id in tickets_db:
            tickets_db[ticket_id]["status"] = "escalated"
            tickets_db[ticket_id]["escalation_reason"] = arguments["reason"]
        return [TextContent(type="text", text=f"Escalated {ticket_id} to human. Reason: {arguments['reason']}")]
    
    elif name == "send_response":
        channel = arguments["channel"]
        msg = arguments["message"]
        if channel == "whatsapp" and len(msg) > 1600:
            msg = msg[:1597] + "..."
        return [TextContent(type="text", text=f"Response sent via {channel}: delivered")]
    
    elif name == "analyze_sentiment":
        message = arguments["message"].lower()
        negative_words = ["angry", "ridiculous", "broken", "terrible", "worst", "hate", "useless", "!!!", "caps"]
        positive_words = ["thank", "great", "love", "excellent", "perfect", "appreciate"]
        neg_count = sum(1 for w in negative_words if w in message)
        pos_count = sum(1 for w in positive_words if w in message)
        if neg_count > pos_count:
            score = max(0.1, 0.5 - (neg_count * 0.1))
        elif pos_count > neg_count:
            score = min(1.0, 0.7 + (pos_count * 0.1))
        else:
            score = 0.5
        return [TextContent(type="text", text=f"Sentiment score: {score:.2f}")]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
