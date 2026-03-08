import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import telebot

# --- Flask Server for Uptime (UptimeRobot နဲ့ ချိတ်ရန်) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    # Render သည် Port 8080 သို့မဟုတ် Dynamic Port ကို သုံးသည်
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Telegram Bot Logic ---
# သင်ပေးထားသော Token ကို အစားထိုးထားသည်
TOKEN = '8796001046:AAG_9A9Fy8DxtpcnmqLnMI9-Cs8F80dguZQ'
bot = telebot.TeleBot(TOKEN)

def get_pin_video(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        # Pinterest link အတို (pin.it) ဖြစ်နေရင် link အရှည်ကို အရင်ယူသည်
        session = requests.Session()
        res = session.get(url, headers=headers, allow_redirects=True)
        
        # Video URL ကို ရှာဖွေခြင်း (Regex pattern ကို ပိုမိုတိကျအောင် ပြင်ထားသည်)
        video_url_match = re.search(r'"video_list":\{"V_720P":\{"url":"(.*?)"', res.text)
        if not video_url_match:
            # တခြား Quality ရှာခြင်း
            video_url_match = re.search(r'"url":"(https://v.pinimg.com/videos/mc/hls/.*?\.mp4)"', res.text)
        
        if video_url_match:
            final_url = video_url_match.group(1).replace('\\u0026', '&')
            return final_url
        return None
    except Exception as e:
        print(f"Error extracting video: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "နေကောင်းလား! Pinterest ဗီဒီယို Link ပေးလိုက်ပါ။ ကျွန်တော် ဒေါင်းပေးပါ့မယ်။ 📥")

@bot.message_handler(func=lambda m: 'pin.it' in m.text or 'pinterest.com' in m.text)
def handle_pinterest(message):
    # စာသားထဲက URL ကို သီးသန့်ထုတ်ယူခြင်း
    try:
        url_match = re.search(r"(?P<url>https?://[^\s]+)", message.text)
        if not url_match:
            return
            
        url = url_match.group("url")
        status_msg = bot.reply_to(message, "ခဏစောင့်ပါ... ဗီဒီယိုကို ပြင်ဆင်နေပါတယ်... ⏳")
        
        video_link = get_pin_video(url)
        
        if video_link:
            bot.delete_message(message.chat.id, status_msg.message_id)
            bot.send_video(message.chat.id, video_link, caption="✅ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။")
        else:
            bot.edit_message_text("စိတ်မရှိပါနဲ့၊ ဗီဒီယို ရှာမတွေ့ပါဘူး။ Link မှန်ရဲ့လား ပြန်စစ်ပေးပါဦး။", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        print(f"Handler error: {e}")

if __name__ == "__main__":
    # Web server ကို အရင်နှိုးမည်
    keep_alive()
    print("Bot is starting with polling...")
    # Bot ကို အဆက်မပြတ် Run စေမည်
    bot.infinity_polling()
