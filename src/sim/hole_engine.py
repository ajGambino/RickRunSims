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
    # Applied at reduced strength - par5_skill is ESPECIALLY dampened to control eagle inflation
    par_adjustment = 0.0
    if hole.par == 3:
        par_adjustment = par3_skill * 0.40
    elif hole.par == 4:
        par_adjustment = par4_skill * 0.40
    elif hole.par == 5:
        # Par-5 skill scaling HEAVILY REDUCED from 0.40 to 0.25 - this is the main eagle source
        par_adjustment = par5_skill * 0.25

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
        "eagle": 0.00001,  # 0.001% - eagles are extremely rare (will be amplified by modifiers)
        "birdie": 0.091,   # 9.1% - birdie rate for pros (slightly increased to preserve scoring)
        "par": 0.75499,    # 75.499% - par is most common
        "bogey": 0.114,    # 11.4% - bogeys happen
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
    # Eagle and birdie are now SEPARATED - they scale differently
    # Eagle is a rare event bucket with minimal skill sensitivity
    # Birdie is the primary scoring upside bucket
    if skill_factor > 0:  # Better than average
        shift = skill_factor * 0.06  # Max 6% shift for elite players
        # Eagle: EXTREMELY minimal skill sensitivity (treat as rare event)
        eagle_shift = shift * 0.003  # AGGRESSIVELY REDUCED from 0.008 to 0.003 - eagles barely scale with skill
        # Birdie: main scoring improvement bucket (compensate for reduced eagle)
        birdie_shift = shift * 0.655  # Slightly increased from 0.65 to maintain scoring

        probs["eagle"] += eagle_shift
        probs["birdie"] += birdie_shift
        probs["par"] -= shift * 0.20
        probs["bogey"] -= shift * 0.35
        probs["double"] -= shift * 0.10
    else:  # Worse than average
        shift = abs(skill_factor) * 0.06
        probs["eagle"] -= shift * 0.001  # AGGRESSIVELY REDUCED from 0.003 to 0.001
        probs["birdie"] -= shift * 0.522
        probs["par"] -= shift * 0.08
        probs["bogey"] += shift * 0.45
        probs["double"] += shift * 0.15

    # Difficulty adjustments: harder holes = fewer birdies, more bogeys
    # Eagle sensitivity is MINIMAL - eagles are rare events on any difficulty
    if difficulty_factor > 0:  # Harder hole
        shift = difficulty_factor * 0.12  # Scale with difficulty
        probs["eagle"] -= shift * 0.003  # AGGRESSIVELY REDUCED from 0.008 to 0.003 - eagles barely affected by difficulty
        probs["birdie"] -= shift * 0.527
        probs["par"] -= shift * 0.07
        probs["bogey"] += shift * 0.40
        probs["double"] += shift * 0.20
    else:  # Easier hole
        shift = abs(difficulty_factor) * 0.12
        probs["eagle"] += shift * 0.005  # AGGRESSIVELY REDUCED from 0.012 to 0.005 - eagles barely affected by difficulty
        probs["birdie"] += shift * 0.645
        probs["par"] -= shift * 0.10
        probs["bogey"] -= shift * 0.35
        probs["double"] -= shift * 0.15

    # Apply player-specific trait boosts (legacy, still supported)
    # These are already small (-0.5 to 0.5), no change needed
    probs["birdie"] += birdie_boost
    probs["bogey"] -= bogey_avoid
    probs["par"] += bogey_avoid - birdie_boost  # Rebalance

    # Aggression: increases eagles/birdies AND bogeys/doubles (risk-reward)
    # Eagle bucket is HEAVILY CAPPED - aggression mainly affects birdie/bogey trade-off
    if aggression > 0:
        agg_shift = aggression * 0.04  # Max 4% shift for max aggression
        # Eagle: EXTREMELY minimal aggression sensitivity - rare event bucket stays capped
        probs["eagle"] += agg_shift * 0.01  # AGGRESSIVELY REDUCED from 0.02 to 0.01 - aggression barely touches eagles
        # Birdie: main upside from aggression (compensate for reduced eagle)
        probs["birdie"] += agg_shift * 0.62  # Increased from 0.61 to preserve risk-reward profile
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
    # Eagle bucket is HEAVILY CAPPED - volatility mainly increases doubles, not eagles
    vol_shift = volatility * 0.02
    # Eagle: EXTREMELY minimal volatility sensitivity - rare event bucket stays capped
    probs["eagle"] += vol_shift * 0.02  # AGGRESSIVELY REDUCED from 0.05 to 0.02 - volatility barely touches eagles
    # Double: main downside from volatility (asymmetric risk profile is OK, compensate for reduced eagle)
    probs["double"] += vol_shift * 0.78  # Increased from 0.75 to preserve volatility character
    probs["par"] -= vol_shift * 0.80

    # Ensure no negative probabilities
    for key in probs:
        probs[key] = max(0.001, probs[key])

    # Normalize to sum to 1.0
    total = sum(probs.values())
    for key in probs:
        probs[key] /= total

    # HARD CAP on eagle probability AFTER normalization to control rare event bucket
    # Target overall eagle rate ~2%, so cap individual hole probabilities aggressively
    MAX_EAGLE_PROB = 0.008  # 0.8% hard cap (very aggressive to hit ~2% tournament average)
    orig_eagle = probs["eagle"]
    if probs["eagle"] > MAX_EAGLE_PROB:
        excess = probs["eagle"] - MAX_EAGLE_PROB
        probs["eagle"] = MAX_EAGLE_PROB
        # Redistribute excess to birdie (preserve scoring upside)
        probs["birdie"] += excess
        # Re-normalize after capping
        total = sum(probs.values())
        for key in probs:
            probs[key] /= total

    # Sample from distribution
    outcomes = ["eagle", "birdie", "par", "bogey", "double"]
    weights = [probs[o] for o in outcomes]

    # DEBUG: Log first 5 holes to audit probability -> outcome pipeline
    if not hasattr(simulate_hole, 'debug_count'):
        simulate_hole.debug_count = 0
    if simulate_hole.debug_count < 5:
        print(f"\n=== HOLE SIMULATION DEBUG #{simulate_hole.debug_count + 1} ===")
        print(f"Player: {player_rating.get('name', 'Unknown')}")
        print(f"Hole: Par {hole.par}, Difficulty {hole.difficulty}")
        print(f"Probabilities passed to sampling:")
        for outcome in outcomes:
            print(f"  {outcome}: {probs[outcome]:.6f} ({probs[outcome]*100:.4f}%)")
        simulate_hole.debug_count += 1

    result = rng.choices(outcomes, weights=weights, k=1)[0]

    # DEBUG: Log sampled outcome
    if simulate_hole.debug_count <= 5:
        print(f"Sampled outcome: {result}")
        print(f"Score: {hole.par - 2 if result == 'eagle' else hole.par - 1 if result == 'birdie' else hole.par if result == 'par' else hole.par + 1 if result == 'bogey' else hole.par + 2}")

    # DEBUG: Track aggregate eagle probability stats
    if not hasattr(simulate_hole, 'eagle_prob_sum'):
        simulate_hole.eagle_prob_sum = 0.0
        simulate_hole.eagle_prob_count = 0
        simulate_hole.eagle_outcome_count = 0
        simulate_hole.total_outcomes = 0
    simulate_hole.eagle_prob_sum += probs["eagle"]
    simulate_hole.eagle_prob_count += 1
    simulate_hole.total_outcomes += 1
    if result == "eagle":
        simulate_hole.eagle_outcome_count += 1

    # Convert to absolute score
    score_map = {
        "eagle": hole.par - 2,
        "birdie": hole.par - 1,
        "par": hole.par,
        "bogey": hole.par + 1,
        "double": hole.par + 2,
    }

    return score_map[result]
