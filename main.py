import os
import re
import requests
from flask import Flask
from threading import Thread
import telebot
from dotenv import load_dotenv

# .env file ကို load လုပ်ခြင်း (Local test အတွက်)
load_dotenv()

# --- Flask Server (Uptime အတွက်) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot Initialization ---
# Token ကို Environment Variable ကနေ တိုက်ရိုက်ယူပါမယ်
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

bot = telebot.TeleBot(TOKEN)

# --- Logic ---
def get_pin_video(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0"}
        res = requests.get(url, headers=headers, allow_redirects=True)
        # ဗီဒီယို URL ရှာခြင်း
        video_url_match = re.search(r'"video_list":\{"V_720P":\{"url":"(.*?)"', res.text)
        if not video_url_match:
            video_url_match = re.search(r'"url":"(https://v.pinimg.com/videos/mc/hls/.*?\.mp4)"', res.text)
        
        return video_url_match.group(1).replace('\\u0026', '&') if video_url_match else None
    except Exception as e:
        print(f"Extraction Error: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Pinterest Downloader Bot အဆင်သင့်ဖြစ်ပါပြီ။ Link ပို့ပေးပါ။ 📥")

@bot.message_handler(func=lambda m: 'pin.it' in m.text or 'pinterest.com' in m.text)
def handle_pinterest(message):
    url_match = re.search(r"(?P<url>https?://[^\s]+)", message.text)
    if not url_match: return
    
    url = url_match.group("url")
    msg = bot.reply_to(message, "ဗီဒီယို ရှာနေပါတယ်... ⏳")
    
    video_link = get_pin_video(url)
    
    if video_link:
        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_video(message.chat.id, video_link, caption="✅ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။")
    else:
        bot.edit_message_text("ဗီဒီယို မတွေ့ပါဘူး။ Link မှန်မမှန် ပြန်စစ်ပေးပါ။", message.chat.id, msg.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
