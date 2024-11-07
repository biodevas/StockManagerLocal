import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

def send_low_stock_alert(beverage_name, current_quantity):
    """Send email alert when beverage stock is low"""
    try:
        smtp_server = os.environ['SMTP_SERVER']
        smtp_port = int(os.environ['SMTP_PORT'])
        smtp_user = os.environ['SMTP_USER']
        smtp_password = os.environ['SMTP_PASSWORD']

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = smtp_user  # Send to the same email address
        msg['Subject'] = f'¡Alerta de Stock Bajo! - {beverage_name}'

        body = f"""
        <html>
            <body>
                <h2>Alerta de Stock Bajo</h2>
                <p>El siguiente producto tiene un nivel de stock bajo:</p>
                <ul>
                    <li><strong>Producto:</strong> {beverage_name}</li>
                    <li><strong>Cantidad actual:</strong> {current_quantity}</li>
                </ul>
                <p>Por favor, reabastezca el inventario pronto.</p>
                <p><small>Enviado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Low stock alert sent successfully for {beverage_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to send low stock alert for {beverage_name}: {str(e)}")
        return False
