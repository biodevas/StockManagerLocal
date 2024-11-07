import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def send_low_stock_alert(beverage_name, current_quantity, user_email='tesoreria@biodevas.org'):
    try:
        logger.info(f"Attempting to send low stock alert for {beverage_name}")
        logger.info(f"Current quantity: {current_quantity}")
        
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
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('SMTP_USER')
        msg['To'] = user_email
        
        # Use standard SMTP settings
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')  # Changed from smtp-relay
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASSWORD')
        
        logger.info(f"Sending from: {smtp_user} to: {user_email}")
        logger.info("Establishing SMTP connection...")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            logger.info("Starting TLS...")
            logger.info(f"Attempting login with user: {smtp_user}")
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            logger.info(f"Email alert sent successfully to {user_email}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending low stock alert: {str(e)}")
        logger.exception("Full traceback:")
        return False
