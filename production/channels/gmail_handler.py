import base64
import re
from email.mime.text import MIMEText
from datetime import datetime
import os
import json

class GmailHandler:
    def __init__(self):
        self.service = None
        self._setup_service()
    
    def _setup_service(self):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
            if os.path.exists(creds_path):
                creds = Credentials.from_authorized_user_file(creds_path)
                self.service = build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"Gmail setup warning: {e}. Using mock mode.")
    
    async def process_notification(self, pubsub_message: dict) -> list:
        if not self.service:
            return [self._mock_email_message()]
        try:
            history_id = pubsub_message.get('historyId')
            history = self.service.users().history().list(
                userId='me',
                startHistoryId=history_id,
                historyTypes=['messageAdded']
            ).execute()
            messages = []
            for record in history.get('history', []):
                for msg_added in record.get('messagesAdded', []):
                    msg_id = msg_added['message']['id']
                    message = await self.get_message(msg_id)
                    messages.append(message)
            return messages
        except Exception as e:
            print(f"Gmail error: {e}")
            return []
    
    def _mock_email_message(self):
        return {
            'channel': 'email',
            'channel_message_id': 'mock_email_001',
            'customer_email': 'test@example.com',
            'subject': 'Test Support Request',
            'content': 'I need help with my account.',
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': 'thread_001',
            'metadata': {'mock': True}
        }
    
    async def get_message(self, message_id: str) -> dict:
        msg = self.service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        body = self._extract_body(msg['payload'])
        return {
            'channel': 'email',
            'channel_message_id': message_id,
            'customer_email': self._extract_email(headers.get('From', '')),
            'subject': headers.get('Subject', ''),
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': msg.get('threadId'),
            'metadata': {'headers': headers}
        }
    
    def _extract_body(self, payload: dict) -> str:
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        return ''
    
    def _extract_email(self, from_header: str) -> str:
        match = re.search(r'<(.+?)>', from_header)
        return match.group(1) if match else from_header
    
    async def send_reply(self, to_email: str, subject: str, body: str, thread_id: str = None) -> dict:
        if not self.service:
            print(f"[MOCK] Email sent to {to_email}: {body[:100]}...")
            return {'channel_message_id': 'mock_sent_001', 'delivery_status': 'sent'}
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_request = {'raw': raw}
        if thread_id:
            send_request['threadId'] = thread_id
        result = self.service.users().messages().send(userId='me', body=send_request).execute()
        return {'channel_message_id': result['id'], 'delivery_status': 'sent'}
