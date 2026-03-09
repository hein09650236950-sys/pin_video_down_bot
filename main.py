import os
import re
import requests
import telebot
from flask import Flask
from threading import Thread

# Flask ကို Web Service အဖြစ် သုံးမှ Port Error မတက်ပါ
app = Flask('')
@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# Bot ကို background မှာ run ပေးခြင်း
Thread(target=run).start()

# Bot ကို စတင်ခြင်း
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def get_pin_video(url):
    api_key = os.environ.get("RAPIDAPI_KEY")
    api_url = "https://pinterest-video-downloader.p.rapidapi.com/dl"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "pinterest-video-downloader.p.rapidapi.com"
    }
    try:
        response = requests.get(api_url, headers=headers, params={"url": url}, timeout=10)
        data = response.json()
        return data.get('url') if 'url' in data else None
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Pinterest Downloader အဆင်သင့်ပါပြီ။ လင့်ခ်ပို့ပေးပါ။")

@bot.message_handler(func=lambda m: True)
def handle_pinterest(message):
    url_match = re.search(r"https?://[^\s]+", message.text)
    if url_match:
        video_link = get_pin_video(url_match.group(0))
        if video_link:
            bot.send_video(message.chat.id, video_link, caption="✅ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။")
        else:
            bot.reply_to(message, "ဗီဒီယို ရှာမတွေ့ပါ။")

if __name__ == "__main__":
    bot.remove_webhook() # Conflict ဖြစ်တာကို ရှင်းပေးမယ်
    bot.infinity_polling(skip_pending=True)
