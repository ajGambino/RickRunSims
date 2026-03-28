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
    # Par-specific skills are modest modifiers (-2 to +2 for par3/4, -3 to +3 for par5)
    # Applied at 40% strength to keep them subtle - they add flavor, not dominance
    par_adjustment = 0.0
    if hole.par == 3:
        par_adjustment = par3_skill * 0.40
    elif hole.par == 4:
        par_adjustment = par4_skill * 0.40
    elif hole.par == 5:
        par_adjustment = par5_skill * 0.40

    # Effective skill for this hole type
    skill = base_skill + par_adjustment

    # Baseline probabilities for a neutral (skill 50) player on a neutral hole
    # Calibrated to PGA Tour averages:
    # - Eagles are rare (1-2%)
    # - Birdies are good but not dominant (18-22%)
    # - Pars are most common (55-60%)
    # - Bogeys happen (15-20%)
    # - Doubles+ are occasional (3-5%)
    baseline = {
        "eagle": 0.00005,  # 0.005% - eagles are extremely rare (will be amplified by modifiers)
        "birdie": 0.090,   # 9% - birdie rate for pros
        "par": 0.75495,    # 75.495% - par is most common
        "bogey": 0.115,    # 11.5% - bogeys happen
        "double": 0.04,    # 4% - doubles are uncommon
    }

    # Adjust for player skill (0-100 scale, normalize to -1 to +1 range)
    # Skill 50 = neutral, 100 = elite, 0 = very weak
    skill_factor = (skill - 50) / 50.0  # Range: -1.0 to +1.0

    # Adjust for hole difficulty (-0.5 to +0.6 typical range)
    difficulty_factor = hole.difficulty

    # Start with baseline
    probs = baseline.copy()

    # Skill adjustments: better players get more birdies/eagles, fewer bogeys/doubles
    # REDUCED from 0.2 to 0.06 - skill effects should be subtle, not dominant
    if skill_factor > 0:  # Better than average
        shift = skill_factor * 0.06  # Max 6% shift for elite players
        probs["eagle"] += shift * 0.03  # Reduced from 0.05 to 0.03
        probs["birdie"] += shift * 0.62
        probs["par"] -= shift * 0.20
        probs["bogey"] -= shift * 0.35
        probs["double"] -= shift * 0.10
    else:  # Worse than average
        shift = abs(skill_factor) * 0.06
        probs["eagle"] -= shift * 0.01  # Reduced from 0.02 to 0.01
        probs["birdie"] -= shift * 0.51
        probs["par"] -= shift * 0.08
        probs["bogey"] += shift * 0.45
        probs["double"] += shift * 0.15

    # Difficulty adjustments: harder holes = fewer birdies, more bogeys
    # REDUCED from 0.3 to 0.12 - difficulty should matter but not dominate
    if difficulty_factor > 0:  # Harder hole
        shift = difficulty_factor * 0.12  # Scale with difficulty
        probs["eagle"] -= shift * 0.03  # Reduced from 0.05 to 0.03
        probs["birdie"] -= shift * 0.50
        probs["par"] -= shift * 0.07
        probs["bogey"] += shift * 0.40
        probs["double"] += shift * 0.20
    else:  # Easier hole
        shift = abs(difficulty_factor) * 0.12
        probs["eagle"] += shift * 0.05  # Reduced from 0.08 to 0.05
        probs["birdie"] += shift * 0.60
        probs["par"] -= shift * 0.10
        probs["bogey"] -= shift * 0.35
        probs["double"] -= shift * 0.15

    # Apply player-specific trait boosts (legacy, still supported)
    # These are already small (-0.5 to 0.5), no change needed
    probs["birdie"] += birdie_boost
    probs["bogey"] -= bogey_avoid
    probs["par"] += bogey_avoid - birdie_boost  # Rebalance

    # Aggression: increases eagles/birdies AND bogeys/doubles (risk-reward)
    # REDUCED from 0.15 to 0.04 - aggression should be noticeable but subtle
    if aggression > 0:
        agg_shift = aggression * 0.04  # Max 4% shift for max aggression
        probs["eagle"] += agg_shift * 0.08  # Reduced from 0.10 to 0.08
        probs["birdie"] += agg_shift * 0.55
        probs["par"] -= agg_shift * 0.83
        probs["bogey"] += agg_shift * 0.15
        probs["double"] += agg_shift * 0.05

    # Consistency: pulls outcomes toward par (compresses distribution)
    # REDUCED from 0.2 to 0.10 - consistency should narrow spread slightly
    if consistency > 0:
        cons_shift = consistency * 0.10  # Max 10% compression for max consistency
        # Move probability mass from extremes toward par
        extreme_reduction = (probs["eagle"] + probs["double"]) * cons_shift
        probs["eagle"] *= (1 - cons_shift)
        probs["double"] *= (1 - cons_shift)
        probs["par"] += extreme_reduction
        # Also slightly reduce birdie/bogey
        minor_reduction = (probs["birdie"] + probs["bogey"]) * (cons_shift * 0.25)
        probs["birdie"] *= (1 - cons_shift * 0.25)
        probs["bogey"] *= (1 - cons_shift * 0.25)
        probs["par"] += minor_reduction

    # Volatility increases extremes (eagles and doubles)
    # REDUCED from 0.1 to 0.02 - volatility should add flavor, not dominate
    vol_shift = volatility * 0.02
    probs["eagle"] += vol_shift * 0.20  # Reduced from 0.25 to 0.20
    probs["double"] += vol_shift * 0.60
    probs["par"] -= vol_shift * 0.80

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
