import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def send_low_stock_alert(beverage_name, current_quantity, user_email='tesoreria@biodevas.org'):
    try:
        logger.info(f"Attempting to send low stock alert for {beverage_name}")
        logger.info(f"SMTP Configuration - Server: {os.getenv('SMTP_SERVER')}, Port: {os.getenv('SMTP_PORT')}")
        logger.info(f"Sending from: {os.getenv('SMTP_USER')} to: {user_email}")
        
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
        
        # Send email using SMTP
        logger.info("Establishing SMTP connection...")
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            logger.info("Starting TLS...")
            server.starttls()
            
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASSWORD')
            
            if not smtp_user or not smtp_pass:
                raise ValueError("SMTP credentials not found in environment variables")
                
            logger.info(f"Attempting login with user: {smtp_user}")
            server.login(smtp_user, smtp_pass)
            
            logger.info("Sending email message...")
            server.send_message(msg)
            
        logger.info(f"Email alert sent successfully to {user_email}")
        return True
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        logger.exception("Full traceback:")
        return False
    except smtplib.SMTPAuthenticationError as auth_error:
        logger.error(f"SMTP Authentication failed: {str(auth_error)}")
        logger.exception("Full traceback:")
        return False
    except Exception as e:
        logger.error(f"Error sending low stock alert: {str(e)}")
        logger.exception("Full traceback:")
        return False
