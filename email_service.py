import smtplib
import ssl
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
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('SMTP_USER')
        msg['To'] = user_email
        
        logger.info(f"Sending from: {os.getenv('SMTP_USER')} to: {user_email}")
        
        # Create SMTP object with SSL context
        context = ssl.create_default_context()
        
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.ehlo()  # Can be omitted
            logger.info("Starting TLS handshake...")
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            logger.info("TLS connection established")
            
            try:
                server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
                logger.info("Login successful")
                server.send_message(msg)
                logger.info(f"Email alert sent successfully to {user_email}")
                return True
            except smtplib.SMTPAuthenticationError as auth_error:
                logger.error(f"SMTP Authentication failed: {auth_error}")
                logger.error("Please ensure you're using an App Password if 2FA is enabled")
                return False
            
    except Exception as e:
        logger.error(f"Error sending low stock alert: {str(e)}")
        logger.exception("Full traceback:")
        return False
