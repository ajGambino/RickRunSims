"""
Hole-level simulation engine.
Simulates a single hole for a single player using rule-based scoring model.
"""
import random
from src.data.schemas import HoleProfile


def simulate_hole(
    player_rating: dict,
    hole: HoleProfile,
    rng: random.Random
) -> int:
    """
    Simulate one hole for one player.

    Uses a simple discrete distribution over score relative to par:
    - Eagle: -2
    - Birdie: -1
    - Par: 0
    - Bogey: +1
    - Double or worse: +2

    Args:
        player_rating: Player rating dict with skill_rating, volatility, birdie_boost, bogey_avoidance
        hole: HoleProfile with par and difficulty
        rng: Random number generator for reproducibility

    Returns:
        Absolute score for the hole (e.g., 3, 4, 5, etc.)
    """
    # Extract player attributes
    skill = player_rating["skill_rating"]  # 0-100 scale
    volatility = player_rating["volatility"]  # 0-1 scale
    birdie_boost = player_rating["birdie_boost"]
    bogey_avoid = player_rating["bogey_avoidance"]

    # Baseline probabilities for a neutral player on a neutral hole
    # These sum to 1.0
    baseline = {
        "eagle": 0.02,
        "birdie": 0.15,
        "par": 0.50,
        "bogey": 0.25,
        "double": 0.08,
    }

    # Adjust for player skill (0-100 scale, normalize to -1 to +1 range)
    # Skill 50 = neutral, 100 = elite, 0 = very weak
    skill_factor = (skill - 50) / 50.0  # Range: -1.0 to +1.0

    # Adjust for hole difficulty (-0.5 to +0.6 typical range)
    difficulty_factor = hole.difficulty

    # Start with baseline
    probs = baseline.copy()

    # Skill adjustments: better players get more birdies/eagles, fewer bogeys/doubles
    if skill_factor > 0:  # Better than average
        shift = skill_factor * 0.2  # Max 20% shift for elite players
        probs["eagle"] += shift * 0.1
        probs["birdie"] += shift * 0.4
        probs["par"] += shift * 0.2
        probs["bogey"] -= shift * 0.5
        probs["double"] -= shift * 0.2
    else:  # Worse than average
        shift = abs(skill_factor) * 0.2
        probs["eagle"] -= shift * 0.1
        probs["birdie"] -= shift * 0.3
        probs["par"] -= shift * 0.1
        probs["bogey"] += shift * 0.3
        probs["double"] += shift * 0.2

    # Difficulty adjustments: harder holes = fewer birdies, more bogeys
    if difficulty_factor > 0:  # Harder hole
        shift = difficulty_factor * 0.3  # Scale with difficulty
        probs["eagle"] -= shift * 0.05
        probs["birdie"] -= shift * 0.3
        probs["par"] -= shift * 0.1
        probs["bogey"] += shift * 0.25
        probs["double"] += shift * 0.2
    else:  # Easier hole
        shift = abs(difficulty_factor) * 0.3
        probs["eagle"] += shift * 0.1
        probs["birdie"] += shift * 0.3
        probs["par"] += shift * 0.1
        probs["bogey"] -= shift * 0.3
        probs["double"] -= shift * 0.2

    # Apply player-specific trait boosts
    probs["birdie"] += birdie_boost
    probs["bogey"] -= bogey_avoid
    probs["par"] += bogey_avoid - birdie_boost  # Rebalance

    # Volatility increases extremes (eagles and doubles)
    vol_shift = volatility * 0.1
    probs["eagle"] += vol_shift
    probs["double"] += vol_shift
    probs["par"] -= vol_shift * 2

    # Ensure no negative probabilities
    for key in probs:
        probs[key] = max(0.001, probs[key])

    # Normalize to sum to 1.0
    total = sum(probs.values())
    for key in probs:
        probs[key] /= total

    # Sample from distribution
    outcomes = ["eagle", "birdie", "par", "bogey", "double"]
    weights = [probs[o] for o in outcomes]
    result = rng.choices(outcomes, weights=weights, k=1)[0]

    # Convert to absolute score
    score_map = {
        "eagle": hole.par - 2,
        "birdie": hole.par - 1,
        "par": hole.par,
        "bogey": hole.par + 1,
        "double": hole.par + 2,
    }

    return score_map[result]
