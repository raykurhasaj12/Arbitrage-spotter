import requests

API_KEY = "59aff4d0ccd1e6954e9131845f2af6c0"

url = "https://api.the-odds-api.com/v4/sports/tennis/odds"

params = {
    "apiKey": API_KEY,
    "regions": "uk",
    "markets": "h2h",
    "oddsFormat": "decimal"
}

response = requests.get(url, params=params)

data = response.json()

for match in data:
    print(match["home_team"], "vs", match["away_team"])
    for bookmaker in match["bookmakers"]:
        print(" ", bookmaker["title"])
        for outcome in bookmaker["markets"][0]["outcomes"]:
            print("   ", outcome["name"], "-", outcome["price"])
    print("---")