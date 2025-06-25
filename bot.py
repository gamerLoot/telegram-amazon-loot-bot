import os
import time
import requests
from bs4 import BeautifulSoup
import telegram

# Load environment variables
BOT_TOKEN = os.getenv("7757825843:AAHLDv4o4scdJ6bOU_qcVBmivcV42OaWMhI")
CHANNEL_ID = os.getenv("https://t.me/loot9T_bot")
TRACKING_ID = os.getenv("loot9t-21")

# Initialize Telegram bot
bot = telegram.Bot(token=BOT_TOKEN)
sent_links = set()

def fetch_deals():
    url = "https://www.amazon.in/s?k=electronics&sort=price-asc-rank"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.select(".s-result-item")

    deals = []

    for item in results:
        title_tag = item.select_one('h2')
        price_tag = item.select_one('.a-price .a-offscreen')
        link_tag = item.select_one('a.a-link-normal')

        if title_tag and price_tag and link_tag:
            title = title_tag.get_text(strip=True)
            price_str = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
            try:
                price = float(price_str)
            except:
                continue

            # Simulated MRP to estimate discount (Amazon doesn't always show MRP)
            estimated_mrp = price * 10  # Fake MRP logic
            discount = ((estimated_mrp - price) / estimated_mrp) * 100

            if discount >= 90:
                link = "https://www.amazon.in" + link_tag['href']
                if link not in sent_links:
                    deals.append((title, price, estimated_mrp, link))

    return deals

def post_to_telegram(deals):
    for title, price, mrp, link in deals:
        if link in sent_links:
            continue

        affiliate_link = link.split("?")[0] + f"?tag={TRACKING_ID}"
        message = f"""🔥 *{title}*
💰 Price: ₹{int(price)} (MRP ~₹{int(mrp)})
📉 Discount: ~{int(((mrp - price) / mrp) * 100)}% OFF
🔗 [Buy Now]({affiliate_link})"""

        try:
            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
            sent_links.add(link)
            time.sleep(2)  # avoid flooding
        except Exception as e:
            print("Telegram error:", e)

# Main loop
while True:
    try:
        deals = fetch_deals()
        if deals:
            post_to_telegram(deals)
        else:
            print("No good deals found at this time.")
    except Exception as e:
        print("Error:", e)
    time.sleep(30)  # run every 30 seconds

