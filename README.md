# NBA Sports Analytics Dashboard

A portfolio project featuring an interactive Power BI dashboard built on live NBA statistics pulled directly from the official NBA Stats API — no third-party subscriptions required.

**Live portfolio:** [cleardatareport.com](https://cleardatareport.com)

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| **League Overview** | Team standings by conference, Win%, offensive/defensive ratings |
| **Player Stats** | Per-game leaderboards for points, rebounds, assists, steals, blocks |
| **Advanced Metrics** | TS%, USG%, PER, Net Rating, PIE — filter by team or position |
| **Game Log** | Recent game results with score trends and streak tracking |
| **Head-to-Head** | Compare any two players across all stat categories |

---

## Project Structure

```
nba_project/
├── data/
│   ├── raw/               # CSVs output by the Python scripts
│   │   ├── player_stats.csv
│   │   ├── team_standings.csv
│   │   ├── game_log.csv
│   │   └── advanced_stats.csv
│   └── processed/         # Reserved for transformed/merged data
├── scripts/
│   ├── run_all.py         # Master refresh script (run this first)
│   ├── fetch_player_stats.py
│   ├── fetch_team_standings.py
│   ├── fetch_game_log.py
│   └── fetch_advanced_stats.py
├── powerbi/               # Place your .pbix file here
├── notebooks/             # Optional EDA notebooks
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Refresh the data

```bash
cd scripts
python run_all.py
```

This fetches fresh data from the NBA Stats API and writes CSVs to `data/raw/`.  
To pull a different season:

```bash
python run_all.py --season 2023-24
```

### 3. Connect Power BI Desktop

1. Open **Power BI Desktop**
2. **Get Data → Text/CSV**
3. Connect to each file in `data/raw/`:
   - `player_stats.csv`
   - `team_standings.csv`
   - `game_log.csv`
   - `advanced_stats.csv`
4. In the **Transform Data** step, promote headers and set data types
5. Save the file as `powerbi/nba_dashboard.pbix`

> **Refreshing data:** After running `run_all.py`, click **Refresh** in Power BI Desktop to pull the updated CSVs. No credentials needed — the data lives locally.

---

## Data Sources

All data is sourced from the **NBA Stats API** (`stats.nba.com`) via the open-source [`nba_api`](https://github.com/swar/nba_api) Python library.

| Dataset | Endpoint | Key Metrics |
|---------|----------|-------------|
| Player Stats | `LeagueDashPlayerStats` | PTS, REB, AST, STL, BLK, FG%, 3PT%, FT% |
| Team Standings | `LeagueStandingsV3` | W, L, Win%, Home/Away record, Streak |
| Game Log | `LeagueGameLog` | Game-by-game results, scores, dates |
| Advanced Stats | `LeagueDashPlayerStats (Advanced)` | TS%, USG%, Net Rating, PIE, Pace |

---

## Suggested Power BI Measures (DAX)

```dax
// Scoring Efficiency
True Shooting % = AVERAGE('player_stats'[Points]) / 
    (2 * (AVERAGE('player_stats'[FG%]) + 0.44 * AVERAGE('player_stats'[FT%])))

// Win Percentage
Win Pct = DIVIDE(SUM('team_standings'[Wins]), 
    SUM('team_standings'[Wins]) + SUM('team_standings'[Losses]))

// Points Differential
Pt Differential = AVERAGE('team_standings'[Pts/Game]) - 
    AVERAGE('team_standings'[Opp Pts/Game])
```

---

## Tech Stack

- **Python 3.11+** — data pipeline
- **nba_api** — NBA Stats API wrapper
- **pandas** — data transformation
- **Power BI Desktop** — visualization

---

## Author

**John Pereyra**  
[cleardatareport.com](https://cleardatareport.com) · [GitHub](https://github.com/Johnsinvi)
