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


def fetch_game_log(season: str = SEASON) -> pd.DataFrame:
    print(f"Fetching game log for {season}...")

    gamelog = leaguegamelog.LeagueGameLog(
        season=season,
        player_or_team_abbreviation="T",  # Team level
        timeout=60,
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
