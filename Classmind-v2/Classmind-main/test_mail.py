import asyncio
import os
from dotenv import load_dotenv
import aiosmtplib
from email.message import EmailMessage

async def test():
    load_dotenv()
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    
    print(f"Testing with: {email}")
    
    msg = EmailMessage()
    msg["Subject"] = "ClassMind Test Mail"
    msg["From"] = email
    msg["To"] = email
    msg.set_content("Hello! If you see this, your ClassMind email setup is working perfectly.")
    
    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            username=email,
            password=password,
            use_tls=False,
            start_tls=True,
        )
        print("\n✅ SUCCESS! The test email has been sent to your own inbox.")
        print("Check your Inbox and Spam folder now.")
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test())
