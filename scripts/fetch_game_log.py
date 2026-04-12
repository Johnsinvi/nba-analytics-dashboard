"""
fetch_game_log.py
Pulls completed game results for the current season from the NBA CDN schedule JSON.
Outputs: data/raw/game_log.csv
"""

import requests
import pandas as pd

OUTPUT_PATH = "../data/raw/game_log.csv"
SCHEDULE_URL = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json"


def fetch_game_log(season: int = None) -> pd.DataFrame:
    print("Fetching game log from NBA CDN...")

    resp = requests.get(SCHEDULE_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    game_dates = data["leagueSchedule"]["gameDates"]

    rows = []
    for gd in game_dates:
        for g in gd["games"]:
            if g.get("gameStatus") != 3:  # 3 = Final
                continue
            home = g["homeTeam"]
            away = g["awayTeam"]
            rows.append({
                "game_id": g["gameId"],
                "Date": g["gameDateEst"][:10],
                "Home Team": home.get("teamTricode", ""),
                "Home Team Name": home.get("teamName", ""),
                "Home Score": home.get("score"),
                "Away Team": away.get("teamTricode", ""),
                "Away Team Name": away.get("teamName", ""),
                "Away Score": away.get("score"),
            })

    df = pd.DataFrame(rows)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df.sort_values("Date", ascending=False, inplace=True)

    return df


if __name__ == "__main__":
    df = fetch_game_log()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} game records to {OUTPUT_PATH}")
