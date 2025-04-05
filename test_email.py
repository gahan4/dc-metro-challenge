"""
Test script for email configuration.
"""
from dc_metro_tracker.utils.email_reporter import send_email
from datetime import datetime

def test_email_config():
    recipient = "neilwgahart@gmail.com"
    subject = "DC Metro Tracker - Test Email"
    body = f"""
    This is a test email from DC Metro Tracker.
    Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    If you're receiving this, your email configuration is working correctly!
    
    Best regards,
    DC Metro Tracker
    """
    
    try:
        send_email(subject, body, recipient)
        print("Test email sent successfully! Please check your inbox.")
    except Exception as e:
        print(f"Error sending test email: {e}")
        print("\nPlease verify your .env file contains:")
        print("- EMAIL_ADDRESS (your Gmail address)")
        print("- EMAIL_APP_PASSWORD (the 16-character app password)")

if __name__ == "__main__":
    test_email_config() 