"""
run_all.py
Master script — runs all data fetchers in sequence and saves CSVs.
Run this before opening Power BI to refresh your data.

Usage:
    python run_all.py
    python run_all.py --season 2023-24
"""

import argparse
import os

from fetch_player_stats import fetch_player_stats
from fetch_team_standings import fetch_team_standings
from fetch_game_log import fetch_game_log
from fetch_advanced_stats import fetch_advanced_stats

RAW_DIR = "../data/raw"


def main(season: str):
    os.makedirs(RAW_DIR, exist_ok=True)

    datasets = {
        "player_stats": fetch_player_stats(season),
        "team_standings": fetch_team_standings(season),
        "game_log": fetch_game_log(season),
        "advanced_stats": fetch_advanced_stats(season),
    }

    for name, df in datasets.items():
        path = os.path.join(RAW_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  Saved {len(df):,} rows -> {path}")

    print("\nAll datasets refreshed successfully.")
    print("You can now open Power BI Desktop and refresh the data source.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh NBA data CSVs")
    parser.add_argument("--season", default="2024-25", help="NBA season (e.g. 2024-25)")
    args = parser.parse_args()
    main(args.season)
