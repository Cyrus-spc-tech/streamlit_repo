# 🐛 Email Service Debugging Guide

## ✅ FIXES APPLIED

### 1. **email_service.py** - Added Comprehensive Debug Logging
- ✅ Every step prints `[EMAIL_SERVICE]` debug messages to console
- ✅ Shows exact error messages (not just generic messages)
- ✅ Validates `session_data` is not None before using
- ✅ Validates session_data is a dict
- ✅ Prints SENDER_EMAIL and masked SENDER_PASSWORD
- ✅ Better exception handling with detailed error context
- ✅ Catches `SMTPNotSupportedError` and `ConnectionError` specifically

### 2. **main.py** - Enhanced /send-report Endpoint
- ✅ Every step prints `[SEND_REPORT]` debug messages to console
- ✅ Validates session exists with error handling
- ✅ Validates email parameter is not empty
- ✅ Validates email format
- ✅ Validates `report` from `compute_report()` is not None
- ✅ Validates report is a dict
- ✅ Ensures report has 'code' field
- ✅ Passes computed `report` (not raw `s`) to send_session_email()
- ✅ Full exception tracking with exc_info=True for logging

### 3. **.env.example** - Clear Instructions
- ✅ Step-by-step Gmail App Password generation guide
- ✅ Explains difference between App Password and regular password
- ✅ Shows password format example

---

## 🎯 HOW TO DEBUG EMAIL ISSUES

### Step 1: Check Console Output
When you send a report, look for these debug lines in your console/terminal:

```
[EMAIL_SERVICE] Starting send_session_email()
[EMAIL_SERVICE] to_email: test@example.com
[EMAIL_SERVICE] teacher_name: John Doe
[EMAIL_SERVICE] Validating SMTP config...
[EMAIL_SERVICE] SENDER_EMAIL: classmind7@gmail.com
[EMAIL_SERVICE] SENDER_PASSWORD: ***
[EMAIL_SERVICE] aiosmtplib available: True
[EMAIL_SERVICE] Connecting to SMTP: smtp.gmail.com:587
[EMAIL_SERVICE] Starting TLS...
[EMAIL_SERVICE] Logging in with email: classmind7@gmail.com
[EMAIL_SERVICE] Sending message...
[EMAIL_SERVICE] SUCCESS: Email sent successfully to test@example.com
```

### Step 2: Check for Error Messages
If you see any `[EMAIL_SERVICE] ERROR` or `[EMAIL_SERVICE] AUTH ERROR`, read the exact message:

| Error Message | Cause | Fix |
|---|---|---|
| `SMTP authentication failed: ...` | Wrong password | Use Gmail App Password (16 chars), not regular password |
| `SMTP not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD` | .env missing variables | Add EMAIL_ADDRESS and EMAIL_PASSWORD to .env |
| `aiosmtplib not installed` | Missing dependency | Run `pip install aiosmtplib` |
| `Connection error to SMTP server` | Network/firewall issue | Check if port 587 is open, or try port 465 |
| `Invalid email address: ...` | Bad email format | Email must have @ and domain (e.g., user@example.com) |
| `Session data is None` | compute_report() failed | Check if session exists and has data |

---

## 🔧 COMMON FIXES

### Issue 1: "Authentication failed"
```
[EMAIL_SERVICE] AUTH ERROR: SMTP authentication failed: (535, b'5.7.8 Username and Password not accepted...')
```

**Solution:**
1. Go to https://myaccount.google.com
2. Click **Security** → **App passwords**
3. Select **Mail** and **Windows Computer**
4. Copy the 16-character password (remove spaces if needed)
5. Update `.env`:
   ```
   EMAIL_ADDRESS=your.email@gmail.com
   EMAIL_PASSWORD=abcdefghijklmnop
   ```
6. Restart FastAPI server
7. Test again

### Issue 2: "SMTP not configured"
```
[EMAIL_SERVICE] ERROR: SMTP not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env
```

**Solution:**
1. Check if `.env` file exists in project root
2. Verify it contains:
   ```
   EMAIL_ADDRESS=your.email@gmail.com
   EMAIL_PASSWORD=your16charapppassword
   ```
3. Make sure there are NO spaces around `=`
4. Restart FastAPI server
5. Test again

### Issue 3: "Connection error to SMTP server"
```
[EMAIL_SERVICE] CONNECTION ERROR: Connection error to SMTP server: [Errno 111] Connection refused
```

**Solution:**
1. Check if Gmail account has 2-Step Verification enabled
2. Try using port 465 instead of 587 (SSL instead of TLS)
3. Update `email_service.py`:
   ```python
   SMTP_PORT = 465
   # And change: await smtp.starttls() to not await starttls()
   ```
4. Check firewall settings
5. Try from a different network

### Issue 4: "Session data is None"
```
[SEND_REPORT] Report computed. Report is None: True
```

**Solution:**
1. Make sure session code is valid
2. Make sure session has data (tasks, students, etc.)
3. Check if `compute_report()` in analytics.py is returning None

---

## 🧪 HOW TO TEST

### Test 1: Manual Test via API
```bash
# Using curl or Postman
POST http://localhost:8000/api/session/ABC123/send-report?email=test@example.com

# Expected success response:
{
    "status": "success",
    "message": "Email sent successfully to test@example.com",
    "email": "test@example.com",
    "session_id": "ABC123"
}
```

### Test 2: Check Console for Debug Messages
Run FastAPI server and watch console:
```bash
uvicorn main:app --reload
```

Look for `[EMAIL_SERVICE]` and `[SEND_REPORT]` messages.

### Test 3: Check Email Inbox
1. Send test email to your own email
2. Check inbox (and Spam folder)
3. Verify HTML formatting is correct

---

## 📋 CHECKLIST

Before going live, verify:

- [ ] `.env` file has `EMAIL_ADDRESS=...` set
- [ ] `.env` file has `EMAIL_PASSWORD=...` set (16-char app password)
- [ ] Gmail account has 2-Step Verification enabled
- [ ] Gmail account has App Passwords enabled
- [ ] FastAPI server is running
- [ ] Firewall allows outbound port 587
- [ ] Manual test API call works (see Test 1 above)
- [ ] Console shows `[EMAIL_SERVICE] SUCCESS` message
- [ ] Email was received in inbox (or Spam folder)

---

## 🔐 SECURITY NOTES

- ✅ Never commit `.env` file to git (use `.gitignore`)
- ✅ App Password is revoked on each device - safe if leaked
- ✅ Email is sent via TLS encryption (port 587)
- ✅ No credentials in logs (password shown as `***`)

---

## 📞 STILL HAVING ISSUES?

1. Check console output for exact `[EMAIL_SERVICE]` error message
2. Copy the exact error message
3. Search for that error in this guide
4. If not found, the error message itself will tell you what's wrong

**Example:**
```
[EMAIL_SERVICE] SMTP ERROR: (550, b'5.1.3 Invalid address. tst@...')
```
→ Check email format (should be user@domain.com)

