import os
import time
import requests
from bs4 import BeautifulSoup
import telegram

# 🔐 Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TRACKING_ID = os.getenv("TRACKING_ID")

# ✅ Initialize Telegram bot
bot = telegram.Bot(token=BOT_TOKEN)

# 🧠 Store sent links to avoid duplicates
sent_links = set()

# 🔎 Amazon scraping function
def fetch_deals():
    url = "https://www.amazon.in/s?k=electronics&rh=p_36%3A100-50000"  # Customize as needed
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for item in soup.select(".s-result-item"):
        title = item.select_one("h2 span")
        link = item.select_one("h2 a")
        price = item.select_one(".a-price-whole")
        mrp = item.select_one(".a-text-price .a-offscreen")

        if not (title and link and price and mrp):
            continue

        try:
            price_value = int(price.text.replace(",", "").strip())
            mrp_value = int(mrp.text.replace("₹", "").replace(",", "").strip())

            discount = 100 - int((price_value / mrp_value) * 100)
            if discount >= 90:
                full_link = f"https://www.amazon.in{link['href'].split('?')[0]}?tag={TRACKING_ID}"
                if full_link not in sent_links:
                    results.append({
                        "title": title.text.strip(),
                        "price": price_value,
                        "mrp": mrp_value,
                        "discount": discount,
                        "link": full_link
                    })
                    sent_links.add(full_link)
        except:
            continue

    return results

# 📤 Send deals to Telegram
def post_to_telegram(deals):
    for deal in deals:
        message = (
            f"🔥 {deal['title']}\n"
            f"💰 Price: ₹{deal['price']} (MRP ₹{deal['mrp']})\n"
            f"📉 Discount: ~{deal['discount']}% OFF\n"
            f"🔗 Buy Now: {deal['link']}"
        )
        bot.send_message(chat_id=CHANNEL_ID, text=message)
        time.sleep(1)

# 🔁 Main loop
while True:
    try:
        print("🔍 Checking for new deals...")
        deals = fetch_deals()
        if deals:
            post_to_telegram(deals)
        else:
            print("No deals found.")
    except Exception as e:
        print(f"❌ Error: {e}")
    time.sleep(30)  # Wait 30 seconds before checking again


