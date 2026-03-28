# Masters Simulation Engine

A tournament simulation project for modeling golf outcomes at the Masters.  
This repository contains the simulation framework, scoring logic, tournament flow, and data interface layers required to run Monte Carlo simulations for major championships.

---

## Important Note on Data

This repository does **not** include any proprietary or licensed tournament or player data.

Some versions of this project may be run locally using private datasets that are not owned by the repository author and are **not redistributed here**.  
Users are responsible for ensuring they have the appropriate rights and permissions to use any data with this project, including compliance with all applicable data ownership, licensing, API, and usage restrictions.

---

## What is Included

- Simulation engine
- Tournament, round, and cut logic
- Data schema and adapter system
- Example workflow using sample/demo data

---

## What is Not Included

- Private PGA or partner data
- Raw event feeds
- Proprietary player level historical datasets
- Sensitive derived outputs based on restricted data

---

## Usage

This project is designed to work with either:

1. Sample/demo data included in `data/sample/`, or
2. User supplied datasets that they are authorized to use

The simulation engine uses a modular data layer, allowing different data sources to be integrated without exposing proprietary datasets.

---

## License & Data Rights

All rights reserved © 2026 AJ Gambino.

No rights are granted to any third-party data, trademarks, or proprietary datasets that may be used outside this repository.  
Any such data remains the property of its respective owners.

---

## Project Overview

This project is designed as a **state based Monte Carlo simulation engine** that models golf tournaments hole by hole using:

- Player specific skill profiles
- Probabilistic outcome modeling
- Tournament progression logic (rounds, cuts, leaderboard dynamics)

The architecture separates:

- **Data ingestion**
- **Feature engineering**
- **Probability modeling**
- **Simulation execution**

This allows the engine to be extended to:

- Different tournaments (PGA Championship, U.S. Open, Open Championship, etc.)
- Different datasets
- Future machine learning based probability models

---

## Future Development

Planned enhancements include:

- Improved hole and shot level modeling
- Course specific calibration
- Weather and condition adjustments
- Player correlation and volatility modeling
- Integration of machine learning based probability models

---

## Example Output

| Player   | Win % | Top 10 % | Make Cut % |
| -------- | ----: | -------: | ---------: |
| Player A |  8.2% |    32.1% |      78.4% |
| Player B |  5.6% |    25.7% |      71.2% |

---

## Quick Start

### Running with Built-in Demo Data

```bash
# Run with default settings (1000 simulations, built-in demo players)
python run.py --tournament masters_2026 --sims 1000

# Run with custom seed for reproducibility
python run.py --tournament masters_2026 --sims 5000 --seed 42

# Show top 10 players only
python run.py --tournament masters_2026 --sims 1000 --top 10
```

### Running with Custom CSV Data

```bash
# Use a custom player CSV file
python run.py --tournament masters_2026 --sims 1000 --player-csv data/demo/players/small_field_demo.csv

# Or use your own CSV file
python run.py --tournament masters_2026 --sims 1000 --player-csv path/to/your/players.csv
```

**Command line options:**
- `--tournament`: Tournament to simulate (default: `masters_2026`)
- `--sims`: Number of Monte Carlo simulations (default: 1000)
- `--seed`: Random seed for reproducibility (optional)
- `--top`: Number of top players to display in results (default: 20)
- `--player-csv`: Path to CSV file with player data (optional, uses built-in demo data if not specified)
- `--export-summary`: Export Monte Carlo summary to CSV file (optional)
- `--export-leaderboard`: Export a representative tournament leaderboard to CSV file (optional)
- `--diagnostics`: Collect and display simulation diagnostics (optional)
- `--export-diagnostics`: Export diagnostics to CSV file (optional)

### CSV File Format

Player CSV files must include these columns:

**Required columns:**
- `player_id`: Unique identifier (string)
- `name`: Player name (string)
- `skill_rating`: Player skill level, 0-100 scale where higher = better (numeric)
- `volatility`: Variance in performance, 0-1 scale where higher = more variance (numeric)

**Optional columns (legacy, still supported):**
- `birdie_boost`: Modifier for birdie probability, -0.5 to 0.5 (numeric, default: 0.0)
- `bogey_avoidance`: Modifier for bogey avoidance, -0.5 to 0.5 (numeric, default: 0.0)

**Optional columns (par-specific skills):**
- `par3_skill`: Skill adjustment for par 3 holes, -15 to 15 (numeric, default: 0.0)
- `par4_skill`: Skill adjustment for par 4 holes, -15 to 15 (numeric, default: 0.0)
- `par5_skill`: Skill adjustment for par 5 holes, -15 to 15 (numeric, default: 0.0)

**Optional columns (play-style traits):**
- `consistency`: Pulls outcomes toward par, 0-1 scale (numeric, default: 0.0)
- `aggression`: Increases eagles/birdies AND bogeys/doubles, 0-1 scale (numeric, default: 0.0)

**Example CSV:**
```csv
player_id,name,skill_rating,volatility,birdie_boost,bogey_avoidance,par3_skill,par4_skill,par5_skill,consistency,aggression
P001,Elite Player,95,0.25,0.12,0.15,2,1,2,0.20,0.30
P002,Strong Contender,88,0.30,0.10,0.12,0,2,4,0.15,0.35
P003,Consistent Pro,82,0.22,0.08,0.14,1,1,1,0.50,0.10
```

Sample CSV files are provided in [data/demo/players/](data/demo/players/).

### Exporting Results

```bash
# Export Monte Carlo summary statistics
python run.py --tournament masters_2026 --sims 1000 --export-summary outputs/summary.csv

# Export a representative tournament leaderboard
python run.py --tournament masters_2026 --sims 1000 --export-leaderboard outputs/leaderboard.csv

# Export both
python run.py --tournament masters_2026 --sims 5000 --seed 42 --export-summary outputs/summary.csv --export-leaderboard outputs/leaderboard.csv
```

**Export formats:**
- **Summary CSV**: Player-level aggregate statistics across all simulations (win %, top 5%, top 10%, make cut %, avg finish, avg score)
- **Leaderboard CSV**: Single representative tournament results showing final standings, round-by-round scores, and cut status

### Simulation Diagnostics

Diagnostics help evaluate whether the simulation produces realistic outcomes by tracking scoring distributions, winning scores, cut lines, and player-level statistics.

```bash
# Display diagnostics in console
python run.py --tournament masters_2026 --sims 1000 --diagnostics

# Export diagnostics to CSV
python run.py --tournament masters_2026 --sims 1000 --export-diagnostics outputs/diagnostics.csv

# Both display and export
python run.py --tournament masters_2026 --sims 5000 --seed 42 --diagnostics --export-diagnostics outputs/diagnostics.csv
```

**Diagnostic metrics tracked:**

*Tournament-level:*
- Average winning score (to par)
- Winning score distribution (min, max, std dev)
- Average cut line (to par)
- Cut line distribution
- Field average score

*Score distribution (all players, all holes):*
- Eagle rate %
- Birdie rate %
- Par rate %
- Bogey rate %
- Double+ rate %

*Player-level (top N players):*
- Average round score to par
- Score standard deviation
- Individual scoring distribution rates

These metrics help answer questions like:
- Are winning scores realistic for the course?
- Is the cut line reasonable?
- Are birdie/bogey rates in line with professional golf?
- Are players too consistent or too volatile?

---

## How It Works

The simulation engine is structured as a modular pipeline that separates data ingestion, feature engineering, probability modeling, and simulation execution.

### 1. Data Layer

Raw data (CSV, API, or private datasets) is loaded through adapter classes and normalized into internal schemas:

- `PlayerProfile`
- `CourseProfile`
- `HoleProfile`
- `TournamentConfig`

This ensures the simulation engine is decoupled from any specific data source.

---

### 2. Feature / Rating Layer

Player and course data are transformed into simulation ready inputs, such as:

- Skill components (OTT, approach by distance, around green, putting)
- Outcome tendencies (birdie, par, bogey rates)
- Accuracy and consistency metrics
- Volatility and course fit adjustments

This layer defines the inputs used by the probability model.

---

### 3. Probability Model (Rule-based / ML)

A probability model converts player and hole inputs into outcome probabilities.

Example output:

    {
        "birdie": 0.22,
        "par": 0.58,
        "bogey": 0.18,
        "double+": 0.02
    }

The current implementation uses rule based logic, but the interface is designed to support future machine learning models without changing the simulation engine.

---

### 4. Simulation Engine (Monte Carlo)

The tournament is simulated hole by hole using probabilistic sampling:

- Each hole outcome is sampled based on player specific probabilities
- Rounds are aggregated from hole results
- Cut rules are applied after the appropriate round
- Final standings are determined after all rounds

This process is repeated thousands of times to estimate outcome distributions.

---

### 5. Output & Aggregation

Results from all simulations are aggregated into:

- Win probabilities
- Top 5 / Top 10 probabilities
- Make cut percentages
- Score distributions

These outputs can be used for analysis, validation, or comparison to market odds.

---

### System Flow

    Raw Data → Adapter → Player/Course Profiles → Feature Layer → Probability Model → Simulation Engine → Aggregated Results

---

## System Architecture

    ┌──────────────┐
    │   Raw Data   │
    │ (CSV / API)  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Adapters   │
    │ (Data Layer) │
    └──────┬───────┘
           │
           ▼
    ┌────────────────────┐
    │  Internal Schemas  │
    │ Player / Course    │
    │ Hole / Tournament  │
    └──────┬─────────────┘
           │
           ▼
    ┌────────────────────┐
    │ Feature / Ratings  │
    │  (Skill Profiles)  │
    └──────┬─────────────┘
           │
           ▼
    ┌────────────────────┐
    │ Probability Model  │
    │ (Rule-based / ML)  │
    └──────┬─────────────┘
           │
           ▼
    ┌────────────────────┐
    │ Simulation Engine  │
    │  (Monte Carlo)     │
    └──────┬─────────────┘
           │
           ▼
    ┌────────────────────┐
    │ Aggregated Results │
    │ Win / Top 10 / Cut │
    └────────────────────┘
