"""
fetch_player_stats.py
Pulls current season player stats from the ESPN sports-core API.
Outputs: data/raw/player_stats.csv
"""

import time
import requests
import pandas as pd

SEASON = 2025
OUTPUT_PATH = "../data/raw/player_stats.csv"
LEADERS_URL = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/seasons/{season}/types/2/leaders?limit=100"
STATS_URL = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/seasons/{season}/types/2/athletes/{athlete_id}/statistics/0"
ATHLETE_URL = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/athletes/{athlete_id}?lang=en&region=us"


def _get(url, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt < retries - 1:
                time.sleep(2)
    return None


def fetch_player_stats(season: int = SEASON) -> pd.DataFrame:
    print(f"Fetching player stats for {season}-{str(season+1)[-2:]}...")

    # Collect unique athlete IDs from leaders endpoint
    leaders_data = _get(LEADERS_URL.format(season=season))
    if not leaders_data:
        return pd.DataFrame()

    athlete_ids = set()
    for cat in leaders_data.get("categories", []):
        for leader in cat.get("leaders", []):
            ref = leader.get("athlete", {}).get("$ref", "")
            if ref:
                aid = ref.split("athletes/")[-1].split("?")[0]
                athlete_ids.add(aid)

    print(f"  Found {len(athlete_ids)} players, fetching stats...")

    rows = []
    for i, aid in enumerate(sorted(athlete_ids)):
        data = _get(STATS_URL.format(season=season, athlete_id=aid))
        if not data:
            continue

        athlete_info = _get(ATHLETE_URL.format(athlete_id=aid))
        name = athlete_info.get("displayName", f"Athlete {aid}") if athlete_info else f"Athlete {aid}"

        row = {"player_id": aid, "Player": name}

        for cat in data.get("splits", {}).get("categories", []):
            for stat in cat.get("stats", []):
                row[stat["name"]] = stat.get("value")

        rows.append(row)

        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(athlete_ids)} done...")
            time.sleep(1)
        else:
            time.sleep(0.15)

    df = pd.DataFrame(rows)

    rename = {
        "avgPoints": "Points",
        "avgRebounds": "Rebounds",
        "avgAssists": "Assists",
        "avgSteals": "Steals",
        "avgBlocks": "Blocks",
        "avgTurnovers": "Turnovers",
        "avgMinutes": "Minutes",
        "gamesPlayed": "Games Played",
        "fieldGoalPct": "FG%",
        "threePtPct": "3PT%",
        "freeThrowPct": "FT%",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    keep = ["player_id", "Player", "Games Played", "Minutes",
            "Points", "Rebounds", "Assists", "Steals", "Blocks",
            "Turnovers", "FG%", "3PT%", "FT%"]
    df = df[[c for c in keep if c in df.columns]]

    return df


if __name__ == "__main__":
    df = fetch_player_stats()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} player records to {OUTPUT_PATH}")
