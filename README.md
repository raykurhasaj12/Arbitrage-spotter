# Arbitrage Spotter

A Python-based sports arbitrage scanner that runs 24/7 on a cloud server, monitors live odds across UK bookmakers, and sends real-time alerts via Telegram when profitable arbitrage opportunities are detected.

## What It Does

Arbitrage betting exploits price discrepancies across bookmakers. By backing all outcomes of an event at different bookmakers, it is possible to guarantee a profit regardless of the result — provided the combined implied probability across the best available odds is below 100%.

This scanner automates the detection of those opportunities across **tennis** markets (chosen for their binary win/loss outcome and continuous availability), pulling live odds from ~20 UK bookmakers and alerting within seconds of a qualifying arb being found.

## How It Works

1. Every 60 seconds, the scanner polls [The Odds API](https://the-odds-api.com/) for live pre-match tennis odds across UK bookmakers
2. For each match, it finds the best available back price on each outcome across all bookmakers
3. It computes the combined implied probability: `(1 / best_home_odds) + (1 / best_away_odds)`
4. If this sum is below `0.99` (i.e. >1% profit margin), an arbitrage exists
5. Optimal stakes are calculated proportionally to guarantee equal return on either outcome
6. An alert is sent to Telegram with the match, bookmakers, odds, stakes, and projected profit

## Stack

- **Python** — core scanner logic
- **The Odds API** — live odds aggregation across UK bookmakers
- **Telegram Bot API** — real-time alert delivery
- **DigitalOcean Droplet** (Ubuntu) — 24/7 cloud hosting via `nohup`

## Key Features

- Pre-match only — in-play events are automatically filtered out
- 1% minimum profit threshold — sub-threshold opportunities are ignored
- Maximum 3 alerts per arb — re-alerts only if profit shifts by >0.5%
- Hourly heartbeat notification confirming the scanner is live
- Graceful error handling — bad API data skips the match rather than crashing

## Arbitrage Formula
Implied Probability = 1 / Decimal Odds
Arb exists when:

(1 / best_odds_outcome_A) + (1 / best_odds_outcome_B) < 1.00
Profit margin = 1 - combined implied probability

## Limitations

This project is framed as a portfolio piece rather than a live trading system. Several structural constraints prevent consistent real-world exploitation:

- **Execution latency** — arbs close within seconds; manual two-leg placement is too slow
- **Polling lag** — the 60-second API interval means opportunities may have moved by the time an alert fires
- **Account attrition** — soft bookmakers restrict or close accounts that arb, degrading the strategy over time
- **Capital requirements** — 1–5% margins require large balances spread across many bookmakers simultaneously to generate meaningful returns

## Skills Demonstrated

- REST API integration and response parsing
- Real-time data pipeline design
- Cloud deployment and process management (DigitalOcean, nohup)
- Financial mathematics — implied probability, stake optimisation
- Robust error handling in long-running automated processes
