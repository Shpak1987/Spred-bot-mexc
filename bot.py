import requests
import time
import telebot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, CHECK_INTERVAL, SPREAD_THRESHOLD, VOLUME_THRESHOLD

bot = telebot.TeleBot(TELEGRAM_TOKEN)
active_alerts = {}

def get_mexc_futures():
    url = "https://contract.mexc.com/api/v1/contract/detail"
    response = requests.get(url).json()
    return {
        item["symbol"].replace("_USDT", ""): {
            "price": float(item["lastPrice"]),
            "url": f"https://futures.mexc.com/exchange/{item['symbol']}"
        }
        for item in response["data"]
    }

def get_dex_pairs():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    response = requests.get(url).json()
    return response.get("pairs", [])

def find_spreads():
    mexc_data = get_mexc_futures()
    dex_pairs = get_dex_pairs()
    found_alerts = {}

    for pair in dex_pairs:
        base_token = pair.get("baseToken", {}).get("symbol", "")
        dex_price = float(pair.get("priceUsd") or 0)
        volume = float(pair.get("volume", {}).get("h24", 0))

        if not base_token or dex_price == 0 or volume < VOLUME_THRESHOLD:
            continue

        if base_token in mexc_data:
            mexc_price = mexc_data[base_token]["price"]
            spread = abs((mexc_price - dex_price) / dex_price) * 100

            if spread >= SPREAD_THRESHOLD:
                dex_link = pair.get("url", "")
                mexc_link = mexc_data[base_token]["url"]
                message = (
                    f"**{base_token}**\n"
                    f"**Спред-шорт {spread:.2f}%**\n"
                    f"[MEXC]({mexc_link})\n"
                    f"[DEX]({dex_link})"
                )
                found_alerts[base_token] = message

    return found_alerts

def send_alerts():
    global active_alerts
    new_alerts = find_spreads()

    for token, message in new_alerts.items():
        if token not in active_alerts:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
            active_alerts[token] = True

    for token in list(active_alerts):
        if token not in new_alerts:
            del active_alerts[token]

if __name__ == "__main__":
    while True:
        try:
            send_alerts()
        except Exception as e:
            print(f"Помилка: {e}")
        time.sleep(CHECK_INTERVAL)
