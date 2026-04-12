"""
fetch_team_standings.py
Pulls current season team standings from the ESPN public standings API.
Outputs: data/raw/team_standings.csv
"""

import requests
import pandas as pd

SEASON = 2025
OUTPUT_PATH = "../data/raw/team_standings.csv"
STANDINGS_URL = "https://site.web.api.espn.com/apis/v2/sports/basketball/nba/standings?season={season}&type=0"


def fetch_team_standings(season: int = SEASON) -> pd.DataFrame:
    print(f"Fetching team standings for {season}-{str(season+1)[-2:]}...")

    resp = requests.get(STANDINGS_URL.format(season=season), timeout=30)
    resp.raise_for_status()
    data = resp.json()

    rows = []
    for conference in data.get("children", []):
        conf_name = conference.get("name", "")
        for entry in conference.get("standings", {}).get("entries", []):
            team = entry.get("team", {})
            row = {
                "team_id": team.get("id"),
                "Team": team.get("abbreviation", ""),
                "Team Name": team.get("displayName", ""),
                "Conference": conf_name,
            }
            for stat in entry.get("stats", []):
                row[stat["name"]] = stat.get("displayValue", stat.get("value"))
            rows.append(row)

    df = pd.DataFrame(rows)

    rename = {
        "wins": "Wins",
        "losses": "Losses",
        "winPercent": "Win%",
        "streak": "Streak",
        "overall": "Record",
        "Home": "Home Record",
        "Road": "Away Record",
        "Last Ten Games": "Last 10",
        "avgPointsFor": "Pts/Game",
        "avgPointsAgainst": "Opp Pts/Game",
        "differential": "Point Diff",
        "playoffSeed": "Seed",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    keep = ["team_id", "Team", "Team Name", "Conference", "Seed",
            "Wins", "Losses", "Win%", "Record", "Streak",
            "Home Record", "Away Record", "Last 10",
            "Pts/Game", "Opp Pts/Game", "Point Diff"]
    df = df[[c for c in keep if c in df.columns]]

    return df


if __name__ == "__main__":
    df = fetch_team_standings()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} team records to {OUTPUT_PATH}")
