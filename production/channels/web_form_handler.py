from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
import uuid

router = APIRouter(prefix="/support", tags=["support-form"])

class SupportFormSubmission(BaseModel):
    name: str
    email: EmailStr
    subject: str
    category: str
    message: str
    priority: Optional[str] = 'medium'

    @validator('name')
    def name_valid(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

    @validator('message')
    def message_valid(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters')
        return v.strip()

    @validator('subject')
    def subject_valid(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Subject must be at least 5 characters')
        return v.strip()

    @validator('category')
    def category_valid(cls, v):
        valid = ['general', 'technical', 'billing', 'feedback', 'bug_report']
        if v not in valid:
            raise ValueError(f'Category must be one of: {valid}')
        return v

class SupportFormResponse(BaseModel):
    ticket_id: str
    message: str
    estimated_response_time: str

@router.post("/submit", response_model=SupportFormResponse)
async def submit_support_form(submission: SupportFormSubmission):
    ticket_id = str(uuid.uuid4())
    message_data = {
        'channel': 'web_form',
        'channel_message_id': ticket_id,
        'customer_email': submission.email,
        'customer_name': submission.name,
        'subject': submission.subject,
        'content': submission.message,
        'category': submission.category,
        'priority': submission.priority,
        'received_at': datetime.utcnow().isoformat(),
        'metadata': {'form_version': '1.0'}
    }
    print(f"[WEB_FORM] New ticket: {ticket_id} from {submission.email}")
    return SupportFormResponse(
        ticket_id=ticket_id,
        message="Thank you! Our AI assistant will respond shortly.",
        estimated_response_time="Usually within 5 minutes"
    )

@router.get("/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    return {
        'ticket_id': ticket_id,
        'status': 'processing',
        'messages': [],
        'created_at': datetime.utcnow().isoformat(),
        'last_updated': datetime.utcnow().isoformat()
    }
