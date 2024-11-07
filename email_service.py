import os
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

logger = logging.getLogger(__name__)

def get_gmail_service():
    """Create and return an authorized Gmail API service instance."""
    try:
        credentials = Credentials.from_authorized_user_info({
            'client_id': os.getenv('GMAIL_CLIENT_ID'),
            'client_secret': os.getenv('GMAIL_CLIENT_SECRET'),
            'refresh_token': os.getenv('GMAIL_REFRESH_TOKEN'),
            'token_uri': 'https://oauth2.googleapis.com/token'
        })
        
        return build('gmail', 'v1', credentials=credentials)
    except Exception as e:
        logger.error(f"Error creating Gmail service: {str(e)}")
        raise

def send_low_stock_alert(beverage_name, current_quantity, user_email='tesoreria@biodevas.org'):
    try:
        # Validate required environment variables
        required_env_vars = ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Create Gmail API service
        service = get_gmail_service()

        # Improved logging
        logger.info(f"Using Gmail API for sending email")
        logger.info(f"From: {os.getenv('SMTP_USER')}")
        logger.info(f"To: {user_email}")
        logger.info(f"Sending low stock alert for {beverage_name} (Quantity: {current_quantity})")

        # Email content
        subject = f'¡Alerta de Stock Bajo! - {beverage_name}'
        body = f'''
        ¡Alerta de Inventario Bajo!
        
        Producto: {beverage_name}
        Cantidad Actual: {current_quantity}
        Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Por favor, reabastezca este producto pronto.
        '''

        # Create message
        message = MIMEText(body)
        message['to'] = user_email
        message['from'] = os.getenv('SMTP_USER')
        message['subject'] = subject

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send email using Gmail API
        logger.info("Sending email via Gmail API...")
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        logger.info(f"Email alert sent successfully to {user_email}")
        return True

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        logger.exception("Full traceback:")
        return False
    except Exception as e:
        logger.error(f"Error sending low stock alert: {str(e)}")
        logger.exception("Full traceback:")
        return False
