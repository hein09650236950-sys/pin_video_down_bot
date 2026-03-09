import os
import re
import requests
from flask import Flask
from threading import Thread
import telebot
from bs4 import BeautifulSoup

# --- အခြေခံ စနစ် ---
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

# --- ဗီဒီယို ဒေါင်းလုဒ် Logic ---
def get_pin_video(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        video_tag = soup.find('meta', property='og:video')
        if video_tag and video_tag.get('content'):
            return video_tag.get('content')
        return None
    except:
        return None

# --- Telegram Command များ ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Pinterest Downloader အဆင်သင့်ပါပြီ။ လင့်ခ်ပို့ပေးပါ။")

@bot.message_handler(func=lambda m: True)
def handle_pinterest(message):
    url_match = re.search(r"https?://[^\s]+", message.text)
    if url_match:
        url = url_match.group(0)
        video_link = get_pin_video(url)
        if video_link:
            bot.send_video(message.chat.id, video_link, caption="✅ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။")
        else:
            bot.reply_to(message, "ဗီဒီယို ရှာမတွေ့ပါ။")

# --- အဓိက အပြောင်းအလဲ ---
if __name__ == "__main__":
    keep_alive()
    # Webhook ကို ကိုယ်တိုင်ဖြုတ်မယ့်အစား polling ကိုပဲ တည်ငြိမ်အောင် သုံးပါ
    bot.infinity_polling(skip_pending=True) 
