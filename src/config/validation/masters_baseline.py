"""
Masters baseline validation benchmarks.

These targets represent realistic Masters tournament outcomes based on historical data.
Values are intentionally ranges or point estimates with tolerances.

These are v1 calibration targets and will be refined as the model improves.
"""

# Tournament-level scoring benchmarks
WINNING_SCORE_TARGET = -14.0  # Target mean winning score (to par)
WINNING_SCORE_RANGE = (-17.0, -11.0)  # Acceptable range for winning scores

CUT_LINE_TARGET = +2.0  # Target mean cut line (to par)
CUT_LINE_RANGE = (-1.0, +5.0)  # Acceptable range for cut line

FIELD_AVG_TARGET = +3.5  # Target field average score (to par)
FIELD_AVG_RANGE = (+2.0, +5.0)  # Acceptable range

# Score distribution benchmarks (percentages)
EAGLE_RATE_TARGET = 1.0  # ~1% eagle rate
EAGLE_RATE_RANGE = (0.5, 1.8)

BIRDIE_RATE_TARGET = 20.0  # ~20% birdie rate
BIRDIE_RATE_RANGE = (17.0, 23.0)

PAR_RATE_TARGET = 62.5  # ~62.5% par rate
PAR_RATE_RANGE = (58.0, 67.0)

BOGEY_RATE_TARGET = 11.0  # ~11% bogey rate
BOGEY_RATE_RANGE = (8.0, 14.0)

DOUBLE_PLUS_RATE_TARGET = 5.5  # ~5.5% double bogey+ rate
DOUBLE_PLUS_RATE_RANGE = (3.0, 8.0)

# Competition structure benchmarks
# Winner concentration: Top player should have reasonable win probability
# (not too concentrated, not too random)
TOP_PLAYER_WIN_PCT_MAX = 25.0  # No single player should win >25% of the time
FIELD_WIN_CONCENTRATION_MIN = 5  # At least 5 players with >2% win probability


def get_benchmark_config():
    """
    Get complete benchmark configuration as a dictionary.

    Returns:
        Dictionary with all benchmark metrics
    """
    return {
        # Tournament-level metrics
        "winning_score": {
            "target": WINNING_SCORE_TARGET,
            "range": WINNING_SCORE_RANGE,
            "units": "strokes to par",
            "description": "Mean winning score across simulations"
        },
        "cut_line": {
            "target": CUT_LINE_TARGET,
            "range": CUT_LINE_RANGE,
            "units": "strokes to par",
            "description": "Mean cut line score"
        },
        "field_avg": {
            "target": FIELD_AVG_TARGET,
            "range": FIELD_AVG_RANGE,
            "units": "strokes to par",
            "description": "Field average score"
        },

        # Score distribution metrics
        "eagle_rate": {
            "target": EAGLE_RATE_TARGET,
            "range": EAGLE_RATE_RANGE,
            "units": "%",
            "description": "Percentage of holes resulting in eagle"
        },
        "birdie_rate": {
            "target": BIRDIE_RATE_TARGET,
            "range": BIRDIE_RATE_RANGE,
            "units": "%",
            "description": "Percentage of holes resulting in birdie"
        },
        "par_rate": {
            "target": PAR_RATE_TARGET,
            "range": PAR_RATE_RANGE,
            "units": "%",
            "description": "Percentage of holes resulting in par"
        },
        "bogey_rate": {
            "target": BOGEY_RATE_TARGET,
            "range": BOGEY_RATE_RANGE,
            "units": "%",
            "description": "Percentage of holes resulting in bogey"
        },
        "double_plus_rate": {
            "target": DOUBLE_PLUS_RATE_TARGET,
            "range": DOUBLE_PLUS_RATE_RANGE,
            "units": "%",
            "description": "Percentage of holes resulting in double bogey or worse"
        },

        # Competition structure (optional, checked separately)
        "top_player_win_pct_max": {
            "target": TOP_PLAYER_WIN_PCT_MAX,
            "units": "%",
            "description": "Maximum win probability for any single player"
        },
        "field_win_concentration_min": {
            "target": FIELD_WIN_CONCENTRATION_MIN,
            "units": "players",
            "description": "Minimum number of players with >2% win probability"
        }
    }
