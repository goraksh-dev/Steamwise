# SteamWise

SteamWise is a Python + Streamlit project for Steam game exploration, budget filtering, heuristic recommendations, and catalogue analytics.

## Features
- Dashboard with dataset metrics and interactive charts
- Budget, genre, tag, rating and review-based recommendations
- Transparent weighted ranking score
- Price analysis and catalogue search
- CSV export of filtered results
- Flexible CSV column detection and basic preprocessing

## Setup (Windows)
1. Install Python 3.10 or newer from https://www.python.org/downloads/
2. Extract this folder.
3. Open Command Prompt in the `SteamWise` folder.
4. Create a virtual environment (recommended):
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. The included `data/steam_games.csv` is the CSV you supplied (308 games, 17 columns). Prices are originally recorded in USD and converted to INR in the app. The dataset has current price, base price, all-time-low price, Steam rating percentage, genres, tags, discount information, multiplayer, and free-game status.
7. Start the app:
   ```bash
   streamlit run app.py
   ```
9. Open the local address Streamlit prints, normally `http://localhost:8501`.

## Dataset notes
Dataset versions use different column names and formats. SteamWise detects common names such as `name`, `current_price_usd`, `steam_rating_pct`, `genres`, `tags`, and `app_id`. Your supplied CSV has no total review-count column. Check the app's columns if your version differs. The app converts source USD prices to INR using an editable exchange rate (default ₹88 per US$1). This is a currency conversion, not a live Indian Steam store price feed.

## Recommendation formula
The score combines genre/tag preference (45%), rating (30%), review strength (15%), and price fit (10%). These are heuristic weights, not a measured accuracy score. Missing or absent columns are handled with neutral/default signals where possible.

## Limitations
- No live Steam API integration or real-time sale price checking
- Historical dataset data may be incomplete or stale
- Recommendations are content-based rankings, not collaborative filtering
