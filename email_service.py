import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def send_low_stock_alert(beverage_name, current_quantity, user_email='tesoreria@biodevas.org'):
    try:
        # Validate required environment variables
        required_env_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Improved logging for SMTP configuration
        logger.info(f"Mail server: {os.getenv('SMTP_SERVER')}:{os.getenv('SMTP_PORT')}")
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

            logger.info(f"Attempting login with user: {smtp_user}")
            try:
                server.login(smtp_user, smtp_pass)
            except smtplib.SMTPAuthenticationError as auth_error:
                if "Application-specific password required" in str(auth_error):
                    logger.error("Gmail requires an application-specific password. Please configure it correctly.")
                raise

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
