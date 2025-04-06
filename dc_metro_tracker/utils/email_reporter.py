"""
Email reporting module for Metro data collection.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from typing import Dict, List
import pandas as pd
from dotenv import load_dotenv

def create_report(db_connection, hours_back: int = 7) -> str:
    """Create a report of train statistics for the last n hours."""
    now = datetime.now()
    start_time = now - timedelta(hours=hours_back)
    
    # Early morning report
    if now.hour == 6:
        return """
        Good morning!
        
        Getting ready to start data collection for the day.
        Collection will run from 6 AM to 10 PM Eastern time.
        
        Best regards,
        DC Metro Tracker
        """
    
    # Query database for statistics
    # (These queries will be implemented once we have data collection running)
    unique_trains = 0  # Placeholder
    metro_center_count = 0  # Placeholder
    line_times = {}  # Placeholder
    
    report = f"""
    DC Metro Statistics Report
    {now.strftime('%Y-%m-%d %H:%M')}
    Covering the past {hours_back} hours
    
    Trains Tracked: {unique_trains}
    Trains through Metro Center: {metro_center_count}
    
    Average Line Transit Times:
    """
    
    for line, time in line_times.items():
        report += f"{line}: {time} minutes\n"
    
    return report

def send_email(subject: str, body: str, recipient: str):
    """Send email using environment configuration."""
    load_dotenv()
    
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv('EMAIL_ADDRESS')
    sender_password = os.getenv('EMAIL_APP_PASSWORD')
    
    if not all([sender_email, sender_password]):
        raise ValueError("Email credentials not found in environment variables")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit() 