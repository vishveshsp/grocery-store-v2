from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from os.path import basename

SERVER_SMTP_HOST = 'localhost'
SERVER_SMTP_PORT = 1025
SENDER_ADDRESS = 'storegrocery68@gmail.com'
SENDER_PASSWORD = 'Cosmonaut911'

from email.mime.image import MIMEImage

def send_email_1(user_email, report_content, graph_io):
    # Create a multipart message container
    msg = MIMEMultipart()
    msg['From'] = SENDER_ADDRESS # Replace with your email address
    msg['To'] = user_email
    msg['Subject'] = 'Monthly Report'

    # Attach the report content
    msg.attach(MIMEText(report_content, 'plain'))

    # Convert BytesIO to MIMEImage and attach it
    graph_io.seek(0)
    img = MIMEImage(graph_io.getvalue(), name='monthly_report.png')
    msg.attach(img)

    # Send the email (code to send email using SMTP goes here)
    s = smtplib.SMTP(host=SERVER_SMTP_HOST, port=SERVER_SMTP_PORT)
    s.login(user = SENDER_ADDRESS, password = SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()


def send_email(to_address, subject, message, attachments = []):
    msg = MIMEMultipart()
    msg['To'] = to_address
    msg['From'] = SENDER_ADDRESS
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'html'))

    for (file, name) in attachments:
        file.seek(0)
        part = MIMEApplication(file.read(), name=name)
        part['Content-Disposition'] = f'attachment; filename="{name}"'
        msg.attach(part)

    s = smtplib.SMTP(host=SERVER_SMTP_HOST, port=SERVER_SMTP_PORT)
    s.login(user = SENDER_ADDRESS, password = SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()

    return True