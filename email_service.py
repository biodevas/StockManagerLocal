from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_gmail_service():
    try:
        logger.info("Creating Gmail service...")
        creds = Credentials.from_authorized_user_info({
            'client_id': os.getenv('GMAIL_CLIENT_ID'),
            'client_secret': os.getenv('GMAIL_CLIENT_SECRET'),
            'refresh_token': os.getenv('GMAIL_REFRESH_TOKEN'),
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/gmail.send']
        })

        if not creds:
            raise ValueError("Could not create credentials. Check environment variables.")

        if creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            creds.refresh(Request())

        service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail service created successfully")
        return service
    except Exception as e:
        logger.error(f"Error creating Gmail service: {str(e)}")
        raise

def send_low_stock_alert(beverage_name, current_quantity, user_email='tesoreria@biodevas.org'):
    try:
        service = create_gmail_service()
        
        # Add logging for debugging
        logger.info(f"Attempting to send low stock alert for {beverage_name}")
        logger.info(f"Current quantity: {current_quantity}")
        logger.info(f"Sending to: {user_email}")
        
        subject = f'¡Alerta de Stock Bajo! - {beverage_name}'
        body = f'''
        ¡Alerta de Inventario Bajo!
        
        Producto: {beverage_name}
        Cantidad Actual: {current_quantity}
        Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Por favor, reabastezca este producto pronto.
        '''
        
        message = MIMEText(body)
        message['to'] = user_email
        message['from'] = 'me'  # Required by Gmail API
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Add more detailed logging
        logger.info("Sending email via Gmail API...")
        result = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        logger.info(f"Email sent successfully. Message ID: {result.get('id')}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending low stock alert: {str(e)}")
        logger.exception("Full traceback:")  # This will log the full stack trace
        return False
