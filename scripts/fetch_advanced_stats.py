"""
fetch_advanced_stats.py
Pulls advanced player metrics (PER, TS%, USG%, etc.) for the current season.
Outputs: data/raw/advanced_stats.csv
"""

import time
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

SEASON = "2024-25"
OUTPUT_PATH = "../data/raw/advanced_stats.csv"


def fetch_advanced_stats(season: str = SEASON) -> pd.DataFrame:
    print(f"Fetching advanced stats for {season}...")

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        measure_type_simple="Advanced",
        per_mode_simple="PerGame",
        timeout=60,
    )
    time.sleep(1)

    df = stats.get_data_frames()[0]
    df.columns = [c.lower() for c in df.columns]

    keep = [
        "player_id", "player_name", "team_abbreviation",
        "gp", "min",
        "e_off_rating", "e_def_rating", "e_net_rating",
        "ast_pct", "ast_to", "oreb_pct", "dreb_pct", "reb_pct",
        "tm_tov_pct", "usg_pct", "ts_pct", "pace",
        "pie",
    ]
    df = df[[c for c in keep if c in df.columns]]

    df.rename(columns={
        "player_name": "Player",
        "team_abbreviation": "Team",
        "gp": "Games Played",
        "min": "Minutes",
        "e_off_rating": "Off Rating",
        "e_def_rating": "Def Rating",
        "e_net_rating": "Net Rating",
        "ast_pct": "AST%",
        "ast_to": "AST/TO",
        "oreb_pct": "OREB%",
        "dreb_pct": "DREB%",
        "reb_pct": "REB%",
        "tm_tov_pct": "TOV%",
        "usg_pct": "USG%",
        "ts_pct": "TS%",
        "pace": "Pace",
        "pie": "PIE",
    }, inplace=True)

    return df


if __name__ == "__main__":
    df = fetch_advanced_stats()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} advanced stat records to {OUTPUT_PATH}")
