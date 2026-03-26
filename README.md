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

## Example Run

```bash
python src/main.py --tournament masters_2026 --sims 10000
```
