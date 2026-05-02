
import os
from dotenv import load_dotenv

def get_google_client_id() -> str:
    val = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1].strip()
    return val

load_dotenv()
cid = get_google_client_id()
print(f"DEBUG_CID_START:{cid}:DEBUG_CID_END")
