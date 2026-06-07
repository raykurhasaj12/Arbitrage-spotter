import requests

API_KEY = "59aff4d0ccd1e6954e9131845f2af6c0"

url = "https://api.the-odds-api.com/v4/sports/mma_mixed_martial_arts/odds"

params = {
    "apiKey": API_KEY,
    "regions": "uk",
    "markets": "h2h",
    "oddsFormat": "decimal"
}

response = requests.get(url, params=params)
data = response.json()

for match in data:
    home = match["home_team"]
    away = match["away_team"]

    # Find the best odds for each player across all bookmakers
    best_home_odds = 0
    best_home_book = ""
    best_away_odds = 0
    best_away_book = ""

    for bookmaker in match["bookmakers"]:
        for outcome in bookmaker["markets"][0]["outcomes"]:
            if outcome["name"] == home:
                if outcome["price"] > best_home_odds:
                    best_home_odds = outcome["price"]
                    best_home_book = bookmaker["title"]
            if outcome["name"] == away:
                if outcome["price"] > best_away_odds:
                    best_away_odds = outcome["price"]
                    best_away_book = bookmaker["title"]

    # The arb detection formula - sum of implied probabilities
    implied_prob = (1 / best_home_odds) + (1 / best_away_odds)

    print(f"{home} vs {away}")
    print(f"  Best {home} odds: {best_home_odds} ({best_home_book})")
    print(f"  Best {away} odds: {best_away_odds} ({best_away_book})")
    print(f"  Implied probability sum: {implied_prob:.4f}")

    if implied_prob < 1:
        profit = (1 - implied_prob) * 100
        print(f"  *** ARB FOUND! Guaranteed profit: {profit:.2f}% ***")
    else:
        print(f"  No arb. Margin: {((implied_prob - 1) * 100):.2f}% in bookmakers favour")
    print("---")