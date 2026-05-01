import requests
import time
import hashlib
import re
from collections import deque

# --- ⚙️ CONFIGURATION ---
API_BASE_URL = "http://203.161.58.20/api/functions/agent-api"
API_KEY = "sk_b331fc25989e09a87e32cd047f13d4ff346696b821c556cb642075d293f8ee35"

BOT_TOKEN = "8679953111:AAF1PsDRXwZRXoWBho8ieooArc8hsxZJpKQ"
CHAT_ID = "-1003869262466" 

POLL_INTERVAL = 5 
FETCH_RECORDS = 100 

seen_otps = deque(maxlen=2000)

def extract_otp(message):
    ig_match = re.search(r'(?i)ig[- ]?(\d+)', message)
    if ig_match: return ig_match.group(1)
    space_match = re.search(r'\b(\d{3})[\s-](\d{3})\b', message)
    if space_match: return space_match.group(1) + space_match.group(2)
    match2 = re.search(r'\b\d{4,8}\b', message)
    return match2.group(0) if match2 else "Copy"

def mask_number(num):
    num = str(num)
    if len(num) > 5:
        return f"{num[:2]}𝑰𝑵𝑺𝑯𝑼𝑩𝑬{num[-3:]}"
    return num

def send_to_telegram(number, platform, message, otp_code_api=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    otp_code = otp_code_api if otp_code_api else extract_otp(message)
    masked_num = mask_number(number)
    
    # --- আপনার দেওয়া অরিজিনাল ডিজাইন ---
    text = f"🌟 <b>𝑰𝑵𝑺 𝑯𝑼𝑩𝑬 𝑶𝑻𝑷</b> 🌟\n\n"
    text += f"💎 <b>𝑺𝒆𝒓𝒗𝒊𝒄𝒆:</b> {platform}\n\n"
    
    text += f"┌───────── • ☎️ • ─────────┐\n"
    text += f"    <code>+{masked_num}</code>\n"
    text += f"└─────────────────────────┘\n\n"
    
    text += f"✨ 𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 <a href='https://t.me/SKYSMSOWNER'>𝐒𝐊𝐘</a> ✨"
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": f"🔑 {otp_code}", "copy_text": {"text": otp_code}},
                {"text": "📝 𝑭𝒖𝒍𝒍 𝑴𝒆𝒔𝒔𝒂𝒈𝒆", "copy_text": {"text": message[:256]}}
            ],
            [
                {"text": "🔥 𝑮𝑬𝑻 𝑵𝑼𝑴𝑩𝑬𝑹 🔥", "url": "https://t.me/INSHUBE_BOT"}
            ],
            [
                {"text": "👨‍💻 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓 𝑺𝑲𝒀", "url": "https://t.me/SKYSMSOWNER"}
            ]
        ]
    }

    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML", 
        "reply_markup": keyboard,
        "disable_web_page_preview": True
    }
    
    try: 
        requests.post(url, json=payload, timeout=10)
    except: 
        pass

def fetch_otps():
    url = f"{API_BASE_URL}/otp"
    headers = {"x-api-key": API_KEY}
    params = {"page": 1, "limit": FETCH_RECORDS}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"): return data.get("data", [])
    except:
        pass
    return []

def main():
    print("🚀 Script Running... (Forwarding OTPs)")
    
    while True:
        otps = fetch_otps()
        
        for otp in reversed(otps):
            raw_msg = otp.get("message_text") or otp.get("sms") or otp.get("message") or otp.get("text") or otp.get("content") or ""
            message = str(raw_msg).strip()
            
            if not message or message.lower() in ['none', 'null', '']:
                continue
                
            number = str(otp.get("number", "Unknown"))
            platform = str(otp.get("platform", "Service"))
            dt = str(otp.get("received_at", "time"))
            otp_code = str(otp.get("otp_code", ""))
            
            raw_string = f"{dt}_{number}_{message}"
            otp_id = hashlib.md5(raw_string.encode()).hexdigest()
            
            if otp_id not in seen_otps:
                send_to_telegram(number, platform, message, otp_code)
                seen_otps.append(otp_id)
                
                # টার্মিনাল লগস
                print(f"✅ Successfully Forwarded OTP: {otp_code}")
                time.sleep(0.5) 
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
