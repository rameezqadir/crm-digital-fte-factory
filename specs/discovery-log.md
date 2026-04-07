# Discovery Log - Incubation Phase

## Date: 2026-04-07

## Patterns Found in Sample Tickets

### Channel Patterns
- Email: Formal tone, longer messages, include context, expect detailed responses
- WhatsApp: Very short messages, casual language, expect instant brief replies
- Web Form: Medium length, structured, expect step-by-step instructions

### Common Topics
1. Password/login issues (30% of tickets)
2. Integration problems (20%)
3. Billing questions (15%) - must escalate
4. Feature requests (10%)
5. API questions (10%)
6. Legal/GDPR (5%) - must escalate
7. Performance/downtime (10%)

### Escalation Triggers Found
- Any pricing question -> immediate escalate
- Legal mentions -> immediate escalate
- Sentiment < 0.3 (angry customers) -> escalate
- Cannot find answer after 2 searches -> escalate

### Edge Cases Discovered
1. Empty messages -> ask for clarification
2. Mixed language messages -> respond in customer's language
3. Very long email chains -> summarize before responding
4. Customer switches channels -> preserve context
5. Bulk requests (CSV errors) -> step-by-step guidance needed
6. Pricing question disguised as feature question -> still escalate
7. API questions that need code examples -> include code snippets in email only
8. Customer provides wrong email -> cannot create proper ticket
9. Attachments referenced but not sent -> ask customer to resend
10. All-caps angry messages -> de-escalate before solving

### Response Length Guidelines (Discovered)
- WhatsApp: 150-200 chars ideal, 300 max
- Email: 200-500 words for complex issues
- Web Form: 100-300 words

### Working System Prompt Key Elements
- Channel metadata in every message
- JSON response format for structured output
- Explicit escalation rules
- Hard constraints listed clearly
