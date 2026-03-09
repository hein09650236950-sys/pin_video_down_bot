import os
import re
import requests
import telebot
from bs4 import BeautifulSoup

# Bot ကို Initialize လုပ်ခြင်း
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ဗီဒီယို ဒေါင်းလုဒ်လုပ်သည့် Function (API သုံးထားသည်)
def get_pin_video(url):
    api_key = os.environ.get("RAPIDAPI_KEY") # Render Environment ထဲက Key ကိုယူမည်
    api_url = "https://pinterest-video-downloader.p.rapidapi.com/dl"
    querystring = {"url": url}
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "pinterest-video-downloader.p.rapidapi.com"
    }
    
    try:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        # API ကပြန်ပေးတဲ့ URL ကိုစစ်ဆေးပြီး Return ပြန်ပေးသည်
        if 'url' in data:
            return data['url']
        return None
    except:
        return None

# Telegram Message များကို ကိုင်တွယ်ခြင်း
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Pinterest Downloader အဆင်သင့်ပါပြီ။ လင့်ခ်ပို့ပေးပါ။")

@bot.message_handler(func=lambda m: True)
def handle_pinterest(message):
    # လင့်ခ်ကို ရှာဖွေခြင်း
    url_match = re.search(r"https?://[^\s]+", message.text)
    if url_match:
        url = url_match.group(0)
        video_link = get_pin_video(url)
        if video_link:
            bot.send_video(message.chat.id, video_link, caption="✅ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။")
        else:
            bot.reply_to(message, "ဗီဒီယို ရှာမတွေ့ပါ။ လင့်ခ်မှန်ကန်မှုရှိမရှိ စစ်ဆေးပေးပါ။")
    else:
        bot.reply_to(message, "ကျေးဇူးပြု၍ Pinterest လင့်ခ်ကိုသာ ပို့ပေးပါ။")

# Bot ကို Run ခြင်း
if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
