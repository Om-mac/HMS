"""
WhatsApp messaging service using Twilio/Wati API.
"""
import logging
from django.conf import settings
from twilio.rest import Client
import requests

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service for sending WhatsApp messages via Twilio or Wati.
    """
    
    def __init__(self, provider='twilio'):
        self.provider = provider
        
        if provider == 'twilio':
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        else:
            self.wati_url = settings.WATI_API_URL
            self.wati_token = settings.WATI_API_TOKEN
    
    def send_message(self, to_number: str, message: str, template_id: str = None) -> dict:
        """
        Send a WhatsApp message.
        
        Args:
            to_number: Recipient's phone number (with country code)
            message: Message body
            template_id: Optional WhatsApp template ID for template messages
            
        Returns:
            Dict with status and message ID
        """
        # Ensure number has country code
        if not to_number.startswith('+'):
            to_number = f'+{to_number}'
        
        if self.provider == 'twilio':
            return self._send_via_twilio(to_number, message, template_id)
        else:
            return self._send_via_wati(to_number, message, template_id)
    
    def _send_via_twilio(self, to_number: str, message: str, template_id: str = None) -> dict:
        """Send message via Twilio WhatsApp API."""
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=f"whatsapp:{to_number}"
            )
            
            logger.info(f"WhatsApp message sent via Twilio: {msg.sid}")
            
            return {
                'success': True,
                'message_id': msg.sid,
                'status': msg.status
            }
        except Exception as e:
            logger.error(f"Failed to send WhatsApp via Twilio: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_via_wati(self, to_number: str, message: str, template_id: str = None) -> dict:
        """Send message via Wati API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.wati_token}',
                'Content-Type': 'application/json'
            }
            
            # Remove + from number for Wati
            clean_number = to_number.replace('+', '')
            
            if template_id:
                # Send template message
                url = f"{self.wati_url}/api/v1/sendTemplateMessage"
                payload = {
                    'whatsappNumber': clean_number,
                    'templateName': template_id,
                    'broadcast_name': 'HMS Notification'
                }
            else:
                # Send session message
                url = f"{self.wati_url}/api/v1/sendSessionMessage/{clean_number}"
                payload = {
                    'messageText': message
                }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"WhatsApp message sent via Wati: {data}")
            
            return {
                'success': True,
                'message_id': data.get('id', ''),
                'status': 'sent'
            }
        except Exception as e:
            logger.error(f"Failed to send WhatsApp via Wati: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_template_message(
        self,
        to_number: str,
        template_name: str,
        template_params: list = None
    ) -> dict:
        """
        Send a pre-approved WhatsApp template message.
        
        Args:
            to_number: Recipient's phone number
            template_name: WhatsApp approved template name
            template_params: List of parameter values for the template
            
        Returns:
            Dict with status and message ID
        """
        if not to_number.startswith('+'):
            to_number = f'+{to_number}'
        
        if self.provider == 'twilio':
            try:
                # Twilio uses content SID for templates
                msg = self.client.messages.create(
                    content_sid=template_name,
                    content_variables=dict(enumerate(template_params or [])),
                    from_=self.from_number,
                    to=f"whatsapp:{to_number}"
                )
                
                return {
                    'success': True,
                    'message_id': msg.sid,
                    'status': msg.status
                }
            except Exception as e:
                logger.error(f"Failed to send template via Twilio: {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            return self._send_via_wati(to_number, '', template_name)


# Singleton instance
whatsapp_service = WhatsAppService(
    provider='twilio' if settings.TWILIO_ACCOUNT_SID else 'wati'
)
