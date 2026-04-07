import os
from datetime import datetime

class WhatsAppHandler:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        self.client = None
        self.validator = None
        self._setup_client()
    
    def _setup_client(self):
        try:
            from twilio.rest import Client
            from twilio.request_validator import RequestValidator
            if self.account_sid and self.auth_token:
                self.client = Client(self.account_sid, self.auth_token)
                self.validator = RequestValidator(self.auth_token)
        except Exception as e:
            print(f"Twilio setup warning: {e}. Using mock mode.")
    
    async def validate_webhook(self, request) -> bool:
        if not self.validator:
            return True  # Allow in mock mode
        try:
            signature = request.headers.get('X-Twilio-Signature', '')
            url = str(request.url)
            form_data = await request.form()
            params = dict(form_data)
            return self.validator.validate(url, params, signature)
        except:
            return False
    
    async def process_webhook(self, form_data: dict) -> dict:
        return {
            'channel': 'whatsapp',
            'channel_message_id': form_data.get('MessageSid', ''),
            'customer_phone': form_data.get('From', '').replace('whatsapp:', ''),
            'content': form_data.get('Body', ''),
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'num_media': form_data.get('NumMedia', '0'),
                'profile_name': form_data.get('ProfileName', ''),
                'wa_id': form_data.get('WaId', ''),
                'status': form_data.get('SmsStatus', '')
            }
        }
    
    async def send_message(self, to_phone: str, body: str) -> dict:
        if not self.client:
            print(f"[MOCK] WhatsApp sent to {to_phone}: {body[:100]}...")
            return {'channel_message_id': 'mock_wa_001', 'delivery_status': 'sent'}
        if not to_phone.startswith('whatsapp:'):
            to_phone = f'whatsapp:{to_phone}'
        messages = self.format_response(body)
        last_result = None
        for msg in messages:
            message = self.client.messages.create(
                body=msg, from_=self.whatsapp_number, to=to_phone
            )
            last_result = {'channel_message_id': message.sid, 'delivery_status': message.status}
        return last_result or {'channel_message_id': 'none', 'delivery_status': 'failed'}
    
    def format_response(self, response: str, max_length: int = 1600) -> list:
        if len(response) <= max_length:
            return [response]
        messages = []
        while response:
            if len(response) <= max_length:
                messages.append(response)
                break
            break_point = response.rfind('. ', 0, max_length)
            if break_point == -1:
                break_point = max_length
            messages.append(response[:break_point + 1].strip())
            response = response[break_point + 1:].strip()
        return messages
