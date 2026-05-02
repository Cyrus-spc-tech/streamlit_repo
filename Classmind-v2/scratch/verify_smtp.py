import asyncio
import os
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText

load_dotenv()

async def test_smtp():
    email = os.getenv("EMAIL_ADDRESS")
    pwd = os.getenv("EMAIL_PASSWORD")
    
    print(f"Testing SMTP for {email}...")
    
    msg = MIMEText("This is a live verification of your ClassMind email system.")
    msg["Subject"] = "🔬 ClassMind Connection Verified"
    msg["From"] = email
    msg["To"] = email
    
    try:
        smtp = aiosmtplib.SMTP(hostname="smtp.gmail.com", port=587, use_tls=False, timeout=15)
        async with smtp:
            await smtp.starttls()
            await smtp.login(email, pwd)
            await smtp.send_message(msg)
        print("✅ SUCCESS: Gmail SMTP is working perfectly!")
        return True
    except Exception as e:
        print(f"❌ FAILURE: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_smtp())
