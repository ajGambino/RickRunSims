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

    Uses a discrete distribution over score relative to par with:
    - Par-type-specific skill adjustments
    - Play-style traits (consistency, aggression)
    - Hole difficulty modifiers

    Score outcomes:
    - Eagle: -2
    - Birdie: -1
    - Par: 0
    - Bogey: +1
    - Double or worse: +2

    Args:
        player_rating: Player rating dict with skill, volatility, par-specific skills, and traits
        hole: HoleProfile with par and difficulty
        rng: Random number generator for reproducibility

    Returns:
        Absolute score for the hole (e.g., 3, 4, 5, etc.)
    """
    # Extract base player attributes
    base_skill = player_rating["skill_rating"]  # 0-100 scale
    volatility = player_rating["volatility"]  # 0-1 scale

    # Extract par-specific skill modifiers
    par3_skill = player_rating.get("par3_skill", 0.0)
    par4_skill = player_rating.get("par4_skill", 0.0)
    par5_skill = player_rating.get("par5_skill", 0.0)

    # Extract play-style traits
    consistency = player_rating.get("consistency", 0.0)  # 0-1 scale
    aggression = player_rating.get("aggression", 0.0)  # 0-1 scale

    # Legacy traits (still supported for backward compatibility)
    birdie_boost = player_rating.get("birdie_boost", 0.0)
    bogey_avoid = player_rating.get("bogey_avoidance", 0.0)

    # Apply par-specific skill adjustment to base skill
    par_adjustment = 0.0
    if hole.par == 3:
        par_adjustment = par3_skill
    elif hole.par == 4:
        par_adjustment = par4_skill
    elif hole.par == 5:
        par_adjustment = par5_skill

    # Effective skill for this hole type
    skill = base_skill + par_adjustment

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

    # Apply player-specific trait boosts (legacy, still supported)
    probs["birdie"] += birdie_boost
    probs["bogey"] -= bogey_avoid
    probs["par"] += bogey_avoid - birdie_boost  # Rebalance

    # Aggression: increases eagles/birdies AND bogeys/doubles (risk-reward)
    if aggression > 0:
        agg_shift = aggression * 0.15  # Max 15% shift for max aggression
        probs["eagle"] += agg_shift * 0.3
        probs["birdie"] += agg_shift * 0.5
        probs["par"] -= agg_shift * 1.0
        probs["bogey"] += agg_shift * 0.15
        probs["double"] += agg_shift * 0.05

    # Consistency: pulls outcomes toward par (compresses distribution)
    if consistency > 0:
        cons_shift = consistency * 0.2  # Max 20% shift for max consistency
        # Move probability mass from extremes toward par
        extreme_reduction = (probs["eagle"] + probs["double"]) * cons_shift
        probs["eagle"] *= (1 - cons_shift)
        probs["double"] *= (1 - cons_shift)
        probs["par"] += extreme_reduction
        # Also slightly reduce birdie/bogey
        minor_reduction = (probs["birdie"] + probs["bogey"]) * (cons_shift * 0.3)
        probs["birdie"] *= (1 - cons_shift * 0.3)
        probs["bogey"] *= (1 - cons_shift * 0.3)
        probs["par"] += minor_reduction

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
