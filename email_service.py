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
    creds = Credentials.from_authorized_user_info({
        'client_id': os.getenv('GMAIL_CLIENT_ID'),
        'client_secret': os.getenv('GMAIL_CLIENT_SECRET'),
        'refresh_token': os.getenv('GMAIL_REFRESH_TOKEN'),
        'token_uri': 'https://oauth2.googleapis.com/token',
        'scopes': ['https://www.googleapis.com/auth/gmail.send']
    })

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)

def send_low_stock_alert(beverage_name, current_quantity, user_email):
    try:
        service = create_gmail_service()
        
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
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        
        logger.info(f"Low stock alert sent for {beverage_name} to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending low stock alert: {str(e)}")
        return False
