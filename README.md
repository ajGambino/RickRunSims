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

## Project Status

**Current Version: v1 (Calibrated)**

The v1 tournament simulation and scoring model are now calibrated and producing realistic results. The focus has shifted to usability, analysis, and presentation.

**Recent Improvements (v1.1):**

- Added large demo field CSV with 90 players
- Added analysis utilities module for inspecting results
- Enhanced CSV export capabilities
- Improved documentation and workflow examples

---

## Future Development

Planned enhancements include:

**Data & Realism:**

- Weather and condition adjustments
- Course-specific calibration for different tournaments
- Historical baseline comparisons

**Modeling:**

- Player correlation and interaction effects
- Enhanced volatility modeling (hot streaks, momentum)
- Shot-level modeling for more granular simulation
- Integration of machine learning based probability models

**Analysis & Output:**

- Interactive visualization tools
- Head-to-head matchup analysis
- Scenario analysis (what-if player conditions)
- Portfolio optimization for betting/DFS applications

**Infrastructure:**

- Web API for simulation service
- Batch processing for large experiments
- Performance optimizations for faster simulation

---

## Output Files

When you export results, the following CSV files are created:

### summary.csv

Player-level aggregate statistics across all simulations:

- `player_id`, `player_name`: Player identifiers
- `win_pct`, `top5_pct`, `top10_pct`: Finish position probabilities
- `make_cut_pct`: Probability of making the cut
- `avg_finish`: Average finish position
- `avg_score`: Average score to par
- `num_sims`: Number of simulations

**Use case:** Identifying favorites, longshots, and value plays

### leaderboard.csv

Single representative tournament results:

- `position`: Final finish position
- `player_id`, `player_name`: Player identifiers
- `total_score`, `score_to_par`: Final scores
- `made_cut`: Whether player made the cut
- `round1`, `round2`, `round3`, `round4`: Round-by-round scores to par

**Use case:** Understanding what a typical tournament outcome looks like

### diagnostics.csv

Simulation calibration and validation metrics:

- Tournament metrics: Winning score, cut line, field average
- Score distribution: Eagle, birdie, par, bogey, double+ rates
- Per-player statistics (for top players)

**Use case:** Validating that simulation produces realistic golf outcomes

### finish_distribution.csv

Enhanced player-level summary with additional finish position breakdowns:

- `player_id`, `player_name`: Player identifiers
- `win_pct`, `top3_pct`, `top5_pct`, `top10_pct`, `top20_pct`: Finish position probabilities
- `make_cut_pct`: Probability of making the cut
- `avg_finish`: Average finish position
- `avg_score`: Average score to par
- `num_sims`: Number of simulations

**Use case:** More granular analysis of finish probabilities for betting or DFS

### sim_results.csv

Individual simulation results (top finishers per simulation):

- `sim_number`: Simulation identifier (1, 2, 3, ...)
- `player_id`, `player_name`: Player identifiers
- `finish_position`: Position in this specific simulation
- `total_score`, `score_to_par`: Final scores
- `made_cut`: Whether player made the cut
- `is_winner`: Whether player won this simulation

**Use case:** Analyzing variance, correlations, and simulation-by-simulation outcomes

---

## Example Output

| Player   | Win % | Top 10 % | Make Cut % |
| -------- | ----: | -------: | ---------: |
| Player A |  8.2% |    32.1% |      78.4% |
| Player B |  5.6% |    25.7% |      71.2% |

---

## Quick Start

### Installation

```bash
# Clone or download the repository
cd RickRunSims

# No external dependencies required - uses Python standard library only
python run.py --help
```

### Running with Built-in Demo Data

```bash
# Run with default settings (1000 simulations, built-in demo players)
python run.py --tournament masters_2026 --sims 1000

# Run with custom seed for reproducibility
python run.py --tournament masters_2026 --sims 5000 --seed 42

# Show top 10 players only
python run.py --tournament masters_2026 --sims 1000 --top 10
```

### Running with Sim-Ready CSV Data

```bash
# Use small demo field (8 players)
python run.py --tournament masters_2026 --sims 1000 --player-csv data/demo/players/small_field_demo.csv

# Use medium demo field (16 players)
python run.py --tournament masters_2026 --sims 1000 --player-csv data/demo/players/masters_2026_demo.csv

# Use large demo field (90 players - realistic Masters field size)
python run.py --tournament masters_2026 --sims 1000 --player-csv data/demo/players/large_field_demo.csv

# Or use your own sim-ready CSV file
python run.py --tournament masters_2026 --sims 1000 --player-csv path/to/your/players.csv
```

### Running with Raw Golf Statistics (Private Data Pipeline)

If you have access to raw PGA Tour statistics (strokes gained, scoring, etc.), you can use the private data pipeline to automatically transform them into simulation-ready features:

```bash
# Use raw player statistics CSV
python run.py --tournament masters_2026 --sims 1000 \
  --raw-player-csv data/private/raw/comprehensive_stats.csv

# Include round-by-round data for better volatility calculation
python run.py --tournament masters_2026 --sims 1000 \
  --raw-player-csv data/private/raw/comprehensive_stats.csv \
  --raw-round-csv data/private/raw/round_performance.csv
```

**Raw Data Pipeline Features:**

- Automatically derives skill_rating from strokes gained (sg_tot, w_sg_tot)
- Computes par-specific skills from sg_par_3, sg_par_4, sg_par_5
- Derives birdie_boost from scoring ability (bob/bobg, sg_app, sg_putt)
- Derives bogey_avoidance from defensive stats (bogey_avoid, scrambling)
- Calculates volatility from round-level variance (when round data provided)
- Applies sample-size shrinkage for players with limited data
- Includes recent-form adjustments from L12/L24 metrics

**Required columns in raw player CSV:**

- `player_id`, `name`, `sg_tot`

**Recommended columns:**

- `w_sg_tot`, `sg_ott`, `sg_app`, `sg_arg`, `sg_putt`
- `sg_par_3`, `sg_par_4`, `sg_par_5`
- `bob`, `bobg`, `bogey_avoid`, `scrambling`
- `gir`, `driving_distance_avg`, `driving_accuracy`
- `rounds`, `sg_rounds`
- `sg_app_l_12`, `sg_ott_l_12`, `sg_putt_l_12` (recent form)

**Round performance CSV columns:**

- `Player`, `TOT` (for volatility calculation)

See [src/data/adapters/private_adapter.py](src/data/adapters/private_adapter.py) for detailed transformation formulas.

**Command line options:**

- `--tournament`: Tournament to simulate (default: `masters_2026`)
- `--sims`: Number of Monte Carlo simulations (default: 1000)
- `--seed`: Random seed for reproducibility (optional)
- `--top`: Number of top players to display in results (default: 20)
- `--player-csv`: Path to sim-ready CSV file with player data (optional, uses demo data if not specified)
- `--raw-player-csv`: Path to raw player statistics CSV (private data pipeline, optional)
- `--raw-round-csv`: Path to raw round-by-round CSV for volatility (used with --raw-player-csv, optional)
- `--export-summary`: Export Monte Carlo summary to CSV file (optional)
- `--export-leaderboard`: Export a representative tournament leaderboard to CSV file (optional)
- `--export-finish-distribution`: Export finish distribution summary with top3/top20 stats to CSV file (optional)
- `--export-sim-results`: Export individual simulation results to CSV file (optional)
- `--sim-results-top`: Number of top finishers per simulation to export (default: 30, only used with --export-sim-results)
- `--diagnostics`: Collect and display simulation diagnostics (optional)
- `--export-diagnostics`: Export diagnostics to CSV file (optional)

### Sim-Ready CSV File Format

Sim-ready player CSV files must include these columns:

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

# Export enhanced finish distribution with top3/top20 breakdowns
python run.py --tournament masters_2026 --sims 1000 --export-finish-distribution outputs/finish_dist.csv

# Export individual simulation results (for variance/correlation analysis)
python run.py --tournament masters_2026 --sims 1000 --export-sim-results outputs/sim_results.csv

# Export all formats
python run.py --tournament masters_2026 --sims 5000 --seed 42 \
  --export-summary outputs/summary.csv \
  --export-leaderboard outputs/leaderboard.csv \
  --export-finish-distribution outputs/finish_dist.csv \
  --export-sim-results outputs/sim_results.csv
```

**Export formats:**

- **Summary CSV**: Player-level aggregate statistics across all simulations (win %, top 5%, top 10%, make cut %, avg finish, avg score)
- **Leaderboard CSV**: Single representative tournament results showing final standings, round-by-round scores, and cut status
- **Finish Distribution CSV**: Enhanced summary with top3 and top20 finish probabilities (useful for betting/DFS)
- **Sim Results CSV**: Individual simulation results showing top finishers per simulation (useful for variance analysis)

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

_Tournament-level:_

- Average winning score (to par)
- Winning score distribution (min, max, std dev)
- Average cut line (to par)
- Cut line distribution
- Field average score

_Score distribution (all players, all holes):_

- Eagle rate %
- Birdie rate %
- Par rate %
- Bogey rate %
- Double+ rate %

_Player-level (top N players):_

- Average round score to par
- Score standard deviation
- Individual scoring distribution rates

These metrics help answer questions like:

- Are winning scores realistic for the course?
- Is the cut line reasonable?
- Are birdie/bogey rates in line with professional golf?
- Are players too consistent or too volatile?

### Analyzing Results

After running simulations and exporting results, use the analysis utilities to inspect distributions and outcomes:

```bash
# Quick summary of simulation results
python -m src.analysis.analyze outputs/summary.csv --command summary

# Analyze top winners
python -m src.analysis.analyze outputs/summary.csv --command winners --top 10

# Analyze cut-making probabilities
python -m src.analysis.analyze outputs/summary.csv --command cuts --threshold 50

# Analyze score distributions
python -m src.analysis.analyze outputs/summary.csv --command scores

# Analyze finish position distributions
python -m src.analysis.analyze outputs/summary.csv --command finishes

# Compare specific players
python -m src.analysis.analyze outputs/summary.csv --command compare --players P001 P002 P003
```

**Available analysis commands:**

- `summary`: Quick overview of simulation results
- `winners`: Top winning probabilities
- `cuts`: Cut-making likelihood analysis
- `scores`: Field score distribution statistics
- `finishes`: Finish position distribution
- `compare`: Side-by-side player comparison

---

## Complete Workflow Example

Here's a complete example from simulation to analysis:

```bash
# 1. Run simulation with large field and export all result formats
python run.py --tournament masters_2026 --sims 5000 --seed 42 \
  --player-csv data/demo/players/large_field_demo.csv \
  --export-summary outputs/summary.csv \
  --export-leaderboard outputs/leaderboard.csv \
  --export-finish-distribution outputs/finish_dist.csv \
  --export-sim-results outputs/sim_results.csv \
  --export-diagnostics outputs/diagnostics.csv \
  --diagnostics

# 2. Analyze the results
python -m src.analysis.analyze outputs/summary.csv --command summary
python -m src.analysis.analyze outputs/summary.csv --command winners --top 15
python -m src.analysis.analyze outputs/summary.csv --command cuts --threshold 75

# 3. Inspect the CSV files in your favorite spreadsheet tool
# - outputs/summary.csv: Player-level aggregate statistics
# - outputs/leaderboard.csv: Sample tournament leaderboard
# - outputs/finish_dist.csv: Enhanced summary with top3/top20 probabilities
# - outputs/sim_results.csv: Individual simulation outcomes (top 30 per sim)
# - outputs/diagnostics.csv: Scoring distribution and calibration metrics
```

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
