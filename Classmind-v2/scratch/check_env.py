import os
from dotenv import load_dotenv
load_dotenv()
print(f"GOOGLE_CLIENT_ID: '{os.getenv('GOOGLE_CLIENT_ID')}'")
