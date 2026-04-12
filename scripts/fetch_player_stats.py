"""
fetch_player_stats.py
Pulls current season player stats from the NBA Stats API via nba_api.
Outputs: data/raw/player_stats.csv
"""

import time
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import players

SEASON = "2025-26"
OUTPUT_PATH = "../data/raw/player_stats.csv"

HEADERS = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Referer": "https://www.nba.com/",
    "Connection": "keep-alive",
}


def fetch_player_stats(season: str = SEASON) -> pd.DataFrame:
    print(f"Fetching player stats for {season}...")

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed="PerGame",
        timeout=60,
        headers=HEADERS,
    )
    time.sleep(1)  # respect NBA API rate limit

    df = stats.get_data_frames()[0]

    # Normalize column names
    df.columns = [c.lower() for c in df.columns]

    # Keep the most relevant columns
    keep = [
        "player_id", "player_name", "team_abbreviation",
        "age", "gp", "min",
        "pts", "reb", "ast", "stl", "blk",
        "tov", "fg_pct", "fg3_pct", "ft_pct",
        "plus_minus",
    ]
    df = df[[c for c in keep if c in df.columns]]

    # Rename for Power BI readability
    df.rename(columns={
        "player_name": "Player",
        "team_abbreviation": "Team",
        "age": "Age",
        "gp": "Games Played",
        "min": "Minutes",
        "pts": "Points",
        "reb": "Rebounds",
        "ast": "Assists",
        "stl": "Steals",
        "blk": "Blocks",
        "tov": "Turnovers",
        "fg_pct": "FG%",
        "fg3_pct": "3PT%",
        "ft_pct": "FT%",
        "plus_minus": "+/-",
    }, inplace=True)

    return df


if __name__ == "__main__":
    df = fetch_player_stats()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} player records to {OUTPUT_PATH}")
