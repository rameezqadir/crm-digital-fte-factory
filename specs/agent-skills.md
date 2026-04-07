# Agent Skills Manifest

## Skill 1: Knowledge Retrieval
- **When to use**: Customer asks product questions
- **Inputs**: query text, optional category filter
- **Outputs**: relevant documentation snippets (max 5 results)
- **Fallback**: Escalate if 2 searches return no results
- **MCP Tool**: search_knowledge_base

## Skill 2: Sentiment Analysis
- **When to use**: Every incoming customer message
- **Inputs**: message text
- **Outputs**: sentiment score (0.0-1.0), label (positive/neutral/negative)
- **Threshold**: Escalate if score < 0.3
- **MCP Tool**: analyze_sentiment

## Skill 3: Escalation Decision
- **When to use**: After generating response, before sending
- **Inputs**: conversation context, sentiment score, message content
- **Outputs**: should_escalate (bool), reason string
- **Hard triggers**: Legal, pricing, refunds, explicit human request
- **MCP Tool**: escalate_to_human

## Skill 4: Channel Adaptation
- **When to use**: Before every outbound message
- **Inputs**: response text, target channel
- **Outputs**: formatted response appropriate for channel
- **Rules**:
  - email: greeting + signature + full detail
  - whatsapp: < 300 chars, casual, emoji ok
  - web_form: semi-formal, numbered steps when applicable

## Skill 5: Customer Identification
- **When to use**: On every incoming message
- **Inputs**: email address, phone number, or web session ID
- **Outputs**: unified customer_id, merged history across all channels
- **MCP Tool**: get_customer_history

## Skill 6: Ticket Management
- **When to use**: Start of every interaction (ALWAYS)
- **Inputs**: customer_id, issue description, channel, priority
- **Outputs**: ticket_id for tracking
- **MCP Tool**: create_ticket
