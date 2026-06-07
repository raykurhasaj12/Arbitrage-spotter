import requests
import time
from datetime import datetime, timezone
import pytz

import os
from dotenv import load_dotenv

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = [8653307657]

LONDON_TZ = pytz.timezone("Europe/London")

SPORTS = [
    "tennis",
    "mma_mixed_martial_arts"
]

MIN_PROFIT_PERCENT = 1.0

EXCLUDED_BOOKMAKERS = {"smarkets"}

arb_alert_count = {}
arb_last_profit = {}
last_heartbeat = None

def send_telegram(message):
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message})

def send_heartbeat():
    global last_heartbeat
    now = datetime.now(LONDON_TZ)
    if last_heartbeat is None or (now - last_heartbeat).seconds >= 3600:
        message = (
            f"✅ ARB SPOTTER ACTIVE\n"
            f"Scanning tennis and MMA every 60 seconds\n"
            f"Minimum profit: {MIN_PROFIT_PERCENT}%\n"
            f"Time: {now.strftime('%d %B %Y at %H:%M London time')}"
        )
        send_telegram(message)
        last_heartbeat = now

def fetch_and_scan(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "uk",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not isinstance(data, list):
        print(f"Unexpected API response for {sport}: {data}")
        return

    for match in data:
        try:
            home = match["home_team"]
            away = match["away_team"]

            commence_time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
            if commence_time < datetime.now(timezone.utc):
                continue

            event_time = commence_time.astimezone(LONDON_TZ).strftime("%A %d %B %Y at %H:%M London time")

            best_home_odds = 0
            best_home_book = ""
            best_away_odds = 0
            best_away_book = ""

            for bookmaker in match["bookmakers"]:
                if bookmaker["key"] in EXCLUDED_BOOKMAKERS:
                    continue

                outcomes = bookmaker["markets"][0]["outcomes"]

                for outcome in outcomes:
                    if outcome["price"] == 0:
                        continue

                    name = outcome["name"]
                    price = outcome["price"]

                    if name == home:
                        if price > best_home_odds:
                            best_home_odds = price
                            best_home_book = bookmaker["title"]
                    elif name == away:
                        if price > best_away_odds:
                            best_away_odds = price
                            best_away_book = bookmaker["title"]

            if best_home_odds == 0 or best_away_odds == 0:
                continue

            implied_prob = (1 / best_home_odds) + (1 / best_away_odds)

            if implied_prob < 1:
                profit = (1 - implied_prob) * 100
                if profit < MIN_PROFIT_PERCENT:
                    continue

                stake = 100
                stake_home = round((stake * (1 / best_home_odds)) / implied_prob)
                stake_away = round((stake * (1 / best_away_odds)) / implied_prob)

                arb_key = f"{home}_{away}_{best_home_book}_{best_away_book}"

                last_profit = arb_last_profit.get(arb_key, None)
                profit_changed = last_profit is None or abs(profit - last_profit) >= 0.5

                if profit_changed:
                    arb_alert_count[arb_key] = 0

                if arb_alert_count.get(arb_key, 0) >= 3:
                    print(f"Arb still present but max alerts reached: {home} vs {away} ({profit:.2f}%)")
                    continue

                detected_at = datetime.now(LONDON_TZ).strftime("%d %B %Y at %H:%M:%S London time")

                message = (
                    f"🚨 ARB FOUND!\n"
                    f"Sport: {sport}\n"
                    f"Match: {home} vs {away}\n"
                    f"Event time: {event_time}\n"
                    f"Bet 1: {home} @ {best_home_odds} with {best_home_book}\n"
                    f"Bet 2: {away} @ {best_away_odds} with {best_away_book}\n"
                    f"Stake {home}: £{stake_home}\n"
                    f"Stake {away}: £{stake_away}\n"
                    f"Guaranteed profit: {profit:.2f}%\n"
                    f"⏰ Detected at: {detected_at}\n"
                    f"⚠️ ALWAYS verify odds on both bookmakers before placing. Odds may have changed.\n"
                    f"Alert {arb_alert_count.get(arb_key, 0) + 1} of 3"
                )

                print(message)
                send_telegram(message)

                arb_alert_count[arb_key] = arb_alert_count.get(arb_key, 0) + 1
                arb_last_profit[arb_key] = profit

        except Exception as e:
            print(f"Error processing match: {e}")
            continue

print("Scanner started.")
print(f"Tennis and MMA: every 60 seconds")
print(f"Minimum profit: {MIN_PROFIT_PERCENT}%")


while True:
    try:
        send_heartbeat()
        for sport in SPORTS:
            fetch_and_scan(sport)
    except Exception as e:
        print(f"Error: {e} - restarting in 60 seconds")
    time.sleep(60)