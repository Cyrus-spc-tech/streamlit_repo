import asyncio
import os
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

async def test_smtp_connection():
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    server = "smtp.gmail.com"
    port = 587

    print(f"--- Email SMTP Connection Test ---")
    print(f"Target Email: {email}")
    print(f"SMTP Server: {server}:{port}")
    
    if not email or not password:
        print("ERROR: EMAIL_ADDRESS or EMAIL_PASSWORD not found in .env")
        return

    # Create a simple message
    message = MIMEMultipart()
    message["From"] = email
    message["To"] = email  # Send to self for testing
    message["Subject"] = "ClassMind SMTP Test"
    message.attach(MIMEText("This is a test email to verify SMTP configuration.", "plain"))

    try:
        print("Connecting to server...")
        smtp = aiosmtplib.SMTP(hostname=server, port=port, use_tls=False, timeout=10)
        
        async with smtp:
            print("Connected. Starting TLS...")
            await smtp.starttls()
            
            print(f"Attempting login for {email}...")
            await smtp.login(email, password)
            
            print("Login successful! Sending test email...")
            await smtp.send_message(message)
            print("Email sent successfully!")
            
        print("\nSUCCESS: Your SMTP configuration is 100% correct.")
        
    except aiosmtplib.SMTPAuthenticationError as e:
        print(f"\nAUTH ERROR: Authentication failed. {e}")
        print("Suggestion: Ensure you are using a 16-character 'App Password', not your regular Gmail password.")
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_smtp_connection())
