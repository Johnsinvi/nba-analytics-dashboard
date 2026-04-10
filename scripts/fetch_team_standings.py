"""
fetch_team_standings.py
Pulls current season team standings from the NBA Stats API.
Outputs: data/raw/team_standings.csv
"""

import time
import pandas as pd
from nba_api.stats.endpoints import leaguestandingsv3

SEASON = "2024-25"
OUTPUT_PATH = "../data/raw/team_standings.csv"


def fetch_team_standings(season: str = SEASON) -> pd.DataFrame:
    print(f"Fetching team standings for {season}...")

    standings = leaguestandingsv3.LeagueStandingsV3(
        season=season,
        timeout=60,
    )
    time.sleep(1)

    df = standings.get_data_frames()[0]
    df.columns = [c.lower() for c in df.columns]

    keep = [
        "teamid", "teamcity", "teamname", "teamabbreviation", "conference",
        "division", "wins", "losses", "winpct", "homerecord", "roadrecord",
        "streak", "l10", "pointspg", "oppointspg",
    ]
    df = df[[c for c in keep if c in df.columns]]

    df.rename(columns={
        "teamcity": "City",
        "teamname": "Team Name",
        "teamabbreviation": "Team",
        "conference": "Conference",
        "division": "Division",
        "wins": "Wins",
        "losses": "Losses",
        "winpct": "Win%",
        "homerecord": "Home Record",
        "roadrecord": "Away Record",
        "streak": "Streak",
        "l10": "Last 10",
        "pointspg": "Pts/Game",
        "oppointspg": "Opp Pts/Game",
    }, inplace=True)

    return df


if __name__ == "__main__":
    df = fetch_team_standings()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} team records to {OUTPUT_PATH}")
