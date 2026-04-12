"""
fetch_game_log.py
Pulls recent game-by-game results for all teams this season.
Outputs: data/raw/game_log.csv
"""

import time
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

SEASON = "2025-26"
OUTPUT_PATH = "../data/raw/game_log.csv"

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


def fetch_game_log(season: str = SEASON) -> pd.DataFrame:
    print(f"Fetching game log for {season}...")

    gamelog = leaguegamelog.LeagueGameLog(
        season=season,
        player_or_team_abbreviation="T",  # Team level
        timeout=60,
        headers=HEADERS,
    )
    time.sleep(1)

    df = gamelog.get_data_frames()[0]
    df.columns = [c.lower() for c in df.columns]

    keep = [
        "game_id", "game_date", "team_abbreviation", "team_name",
        "matchup", "wl", "pts", "reb", "ast", "stl", "blk",
        "tov", "fg_pct", "fg3_pct", "ft_pct", "plus_minus",
    ]
    df = df[[c for c in keep if c in df.columns]]

    df.rename(columns={
        "game_date": "Date",
        "team_abbreviation": "Team",
        "team_name": "Team Name",
        "matchup": "Matchup",
        "wl": "W/L",
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

    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", ascending=False, inplace=True)

    return df


if __name__ == "__main__":
    df = fetch_game_log()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} game records to {OUTPUT_PATH}")
