import smtplib
from email.message import EmailMessage
from config import smtp_server, smtp_port, smtp_user, smtp_password, email_template_path, password_reset_email_template_path, website_email_template_path
from logging_utils import log_success, log_error
from mongo_utils import client
import re
import datetime

def send_recovery_email(email, username, password):
    try:
        with open(email_template_path, 'r') as file:
            email_template_content = file.read()

        email_content = email_template_content.replace("{username}", username).replace("{password}", password)

        msg = EmailMessage()
        msg['Subject'] = "Temporary Password - Blahaj.land"
        msg['From'] = smtp_user
        msg['To'] = email
        msg.set_content(email_content, subtype='html')

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        log_success(f"Password sent to {email}.")
    except Exception as e:
        log_error(f"Failed to send email: {e}")

def send_password_reset_email(email, username, reset_link):
    try:
        with open(password_reset_email_template_path, 'r') as file:
            email_template_content = file.read()

        email_content = email_template_content.replace("{username}", username).replace("{reset_link}", reset_link)

        msg = EmailMessage()
        msg['Subject'] = "Password Reset Link - Blahaj.land"
        msg['From'] = smtp_user
        msg['To'] = email
        msg.set_content(email_content, subtype='html')

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        log_success(f"Password reset link sent to {email}.")
    except Exception as e:
        log_error(f"Failed to send password reset email: {e}")

# this is straight up broken
def send_website_setup_email(email, username, case, line1, line2, line3, link, buttontext):
    try:
        with open('website_email_template.html', 'r') as file:
            email_template_content = file.read()

        email_content = email_template_content.replace("{username}", username)\
                                              .replace("{case}", case)\
                                              .replace("{line1}", line1)\
                                              .replace("{line2}", line2)\
                                              .replace("{line3}", line3)\
                                              .replace("{link}", link)\
                                              .replace("{buttontext}", buttontext)

        msg = EmailMessage()
        msg['Subject'] = "Website Setup - Blahaj.land"
        msg['From'] = smtp_user
        msg['To'] = email
        msg.set_content(email_content, subtype='html')

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        log_success(f"Website setup email sent to {email}.")
    except Exception as e:
        log_error(f"Failed to send website setup email: {e}")