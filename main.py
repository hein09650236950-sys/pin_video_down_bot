import os
import re
import requests
from flask import Flask
from threading import Thread
import telebot

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
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- Logic: Video Extraction ---
def get_pin_video(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=10)
        
        # Pattern 1: video_list နေရာကနေ ရှာခြင်း
        video_url = re.search(r'"video_list":\{"V_720P":\{"url":"(.*?)"', res.text)
        if video_url:
            return video_url.group(1).replace('\\u0026', '&')
            
        # Pattern 2: အကယ်၍ ပုံမှန် link မတွေ့ရင် နောက်ထပ်နည်းလမ်းတစ်ခု
        match = re.search(r'https://v\.pinimg\.com/videos/mc/.*?\.mp4', res.text)
        if match:
            return match.group(0)
            
        return None
    except Exception as e:
        print(f"Error in extraction: {e}")
        return None

# --- Telegram Bot Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Pinterest Video Downloader အဆင်သင့်ဖြစ်ပါပြီ။ Link ပို့ပေးပါ။ 📥")

@bot.message_handler(func=lambda m: True)
def handle_pinterest(message):
    if 'pin.it' in message.text or 'pinterest.com' in message.text:
        url_match = re.search(r"(?P<url>https?://[^\s]+)", message.text)
        if not url_match: return
        
        url = url_match.group("url")
        msg = bot.reply_to(message, "ဗီဒီယို ရှာနေပါတယ်... ⏳")
        
        video_link = get_pin_video(url)
        
        if video_link:
            try:
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_video(message.chat.id, video_link, caption="✅ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။")
            except:
                bot.edit_message_text(f"ဗီဒီယိုလင့်ခ် ရပါပြီ: {video_link}", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("ဗီဒီယို ရှာမတွေ့ပါဘူး။ ပုဂ္ဂလိက (Private) Video ဖြစ်နေတာလား စစ်ပေးပါ။", message.chat.id, msg.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
