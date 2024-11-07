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
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('SMTP_USER')
        msg['To'] = user_email
        
        logger.info(f"Sending from: {os.getenv('SMTP_USER')} to: {user_email}")
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            logger.info("TLS started")
            
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
