import os
import requests
from flask import Flask
from threading import Thread
import telebot
from bs4 import BeautifulSoup

# --- Uptime Server ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is active!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot Initialization ---
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- Video Logic ---
def get_pin_video(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Video tag ကို ရှာခြင်း
        video_tag = soup.find('video')
        if video_tag and video_tag.get('src'):
            return video_tag.get('src')
        
        # Meta tag ကနေ ရှာခြင်း
        meta_tag = soup.find('meta', property='og:video')
        if meta_tag:
            return meta_tag.get('content')
            
        return None
    except:
        return None

@bot.message_handler(func=lambda m: 'pin' in m.text)
def handle_pinterest(message):
    url_match = re.search(r"(?P<url>https?://[^\s]+)", message.text)
    if url_match:
        video_link = get_pin_video(url_match.group("url"))
        if video_link:
            bot.send_video(message.chat.id, video_link, caption="✅ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။")
        else:
            bot.reply_to(message, "ဗီဒီယို ရှာမတွေ့ပါ။ အခြားလင့်ခ်တစ်ခု စမ်းကြည့်ပါ။")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
