# Masters Simulation Engine

A calibrated Monte Carlo golf tournament simulation engine that models events hole-by-hole, applies real tournament structure, and produces realistic scoring distributions and outcomes.

Built to simulate major championships like the Masters with realistic:

- scoring distributions
- cut dynamics
- player performance hierarchy

---

## Validation Snapshot (Masters 2026, 5,000 sims)

- Winning Score: -13.97
- Cut Line: +3.36
- Field Average: +2.35

**Score Distribution:**

- Eagle: 0.99%
- Birdie: 19.94%
- Par: 59.35%
- Bogey: 13.68%
- Double+: 6.04%

All 10 validation checks passed.

---

## Quick Start

### Installation

```bash
cd RickRunSims
python run.py --help
```

### Run with Demo Data

```bash
python run.py --tournament masters_2026 --sims 1000
```

### Reproducible Run

```bash
python run.py --tournament masters_2026 --sims 5000 --seed 42
```

### Run with Your Own Data

```bash
python run.py --tournament masters_2026 --sims 1000 \
  --player-csv path/to/your/players.csv
```

---

## Design Philosophy

This project prioritizes:

- realism over complexity
- calibration over theory
- end-to-end correctness (hole → round → tournament)

Rather than relying on black-box models, the engine is built to:

- explicitly control scoring distributions
- enforce tournament structure (cuts, rounds)
- validate outputs against real-world benchmarks

The system is designed to support future ML models, but does not depend on them.

---

## Important Note on Data

This repository does **not** include any proprietary or licensed tournament or player data.

Some versions of this project may be run locally using private datasets that are not owned by the repository author and are **not redistributed here**.

Users are responsible for ensuring they have the appropriate rights and permissions to use any data with this project.

---

## Project Overview

This project is a **state-based Monte Carlo simulation engine** that models golf tournaments hole-by-hole using:

- player-specific skill profiles
- probabilistic outcome modeling
- tournament progression logic (rounds, cuts, leaderboard dynamics)

The architecture separates:

- data ingestion
- feature engineering
- probability modeling
- simulation execution

This allows extension to:

- different tournaments
- different datasets
- machine learning probability models

---

## Project Status

**Current Version: v1 (Calibrated & Validated)**

The simulation is calibrated against real-world scoring benchmarks and passes validation for:

- winning score
- cut line
- field scoring distribution
- hole-level outcome frequencies

Focus has shifted to usability, analysis, and presentation.

---

## What is Included

- simulation engine
- tournament, round, and cut logic
- data schema and adapter system
- demo data workflow

---

## What is Not Included

- proprietary PGA or partner data
- raw event feeds
- private historical datasets
- restricted derived outputs

---

## Output Files

Each run produces structured outputs:

### summary.csv

Player-level aggregate statistics:

- win %, top finishes, make cut %
- average finish and score

### leaderboard.csv

Representative tournament:

- final standings
- round-by-round scores
- cut status

### finish_dist.csv

Expanded finish probabilities:

- top 3 / top 5 / top 10 / top 20

### sim_results.csv

Per-simulation results:

- finish positions
- scores
- winners

### diagnostics.csv

Calibration metrics:

- winning score
- cut line
- field average
- scoring distribution

### validation/

- validation_summary.csv
- validation_report.txt
- validation_report.json

---

## Simulation Diagnostics

Diagnostics evaluate realism across:

**Tournament-level:**

- winning score distribution
- cut line distribution
- field average

**Hole-level distribution:**

- eagle, birdie, par, bogey, double+ rates

**Player-level:**

- average round score
- variance
- outcome frequencies

---

## Example Workflow

```bash
python run.py --tournament masters_2026 --sims 5000 --seed 42 \
  --player-csv data/demo/players/large_field_demo.csv \
  --export-summary outputs/summary.csv \
  --export-leaderboard outputs/leaderboard.csv \
  --export-finish-distribution outputs/finish_dist.csv \
  --export-sim-results outputs/sim_results.csv \
  --export-diagnostics outputs/diagnostics.csv \
  --diagnostics
```

Then analyze:

```bash
python -m src.analysis.analyze outputs/summary.csv --command summary
python -m src.analysis.analyze outputs/summary.csv --command winners --top 15
```

---

## Raw Data Pipeline (Optional)

Supports transforming raw golf statistics into simulation-ready inputs:

```bash
python run.py --tournament masters_2026 --sims 1000 \
  --raw-player-csv data/private/raw/comprehensive_stats.csv \
  --raw-round-csv data/private/raw/round_performance.csv
```

Features:

- skill rating from strokes gained
- par-specific adjustments
- birdie / bogey tendencies
- volatility from round data
- sample-size shrinkage
- recent form adjustments

---

## How It Works

### 1. Data Layer

Adapters normalize raw data into internal schemas.

### 2. Feature Layer

Transforms inputs into skill profiles and tendencies.

### 3. Probability Model

Generates outcome probabilities per hole.

### 4. Simulation Engine

Runs hole-by-hole Monte Carlo simulation.

### 5. Aggregation

Produces win %, cut %, and scoring distributions.

---

## System Flow

Raw Data → Adapter → Player/Course Profiles → Feature Layer → Probability Model → Simulation → Results

---

## System Architecture

Raw Data  
↓  
Adapters  
↓  
Schemas  
↓  
Feature Layer  
↓  
Probability Model  
↓  
Simulation Engine  
↓  
Aggregated Results

---

## Future Development

**Data & Realism**

- weather adjustments
- course-specific calibration

**Modeling**

- player correlations
- volatility improvements
- ML probability models

**Analysis**

- visualization tools
- scenario analysis
- DFS/betting applications

**Infrastructure**

- API layer
- batch simulations
- performance optimization

---

## License & Data Rights

All rights reserved © 2026 AJ Gambino.

No rights are granted to any third-party data used outside this repository.
