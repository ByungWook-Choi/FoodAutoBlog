import urllib.request
import urllib.parse
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Telegram Bot Token is not set. Skipping notification.")
        return False
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': text}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            print("텔레그램 알림 발송 성공!")
            return True
    except Exception as e:
        print(f"텔레그램 알림 발송 실패: {e}")
        return False
