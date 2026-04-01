"""
Hole-level simulation engine.
Simulates a single hole for a single player using rule-based scoring model.
"""
import random
from src.data.schemas import HoleProfile

DEBUG_HOLE_SIM = False


def simulate_hole(
    player_rating: dict,
    hole: HoleProfile,
    rng: random.Random
) -> tuple[int, str]:
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
        Tuple of (absolute_score, outcome_category)
        - absolute_score: integer stroke count (e.g., 3, 4, 5, etc.)
        - outcome_category: "eagle", "birdie", "par", "bogey", or "double"
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
    # Par skills are on -3/+3 scale, need to scale to match skill_rating's 0-100 scale
    par_adjustment = 0.0
    if hole.par == 3:
        par_adjustment = par3_skill * 4.0  # 2.0 par skill → +12 skill points
    elif hole.par == 4:
        par_adjustment = par4_skill * 4.0  # 2.0 par skill → +12 skill points
    elif hole.par == 5:
        par_adjustment = par5_skill * 2.5  # 3.0 par skill → +12 skill points (wider input range)

    # Effective skill for this hole type
    skill = base_skill + par_adjustment

    # Baseline probabilities for a neutral (skill 50) player on a neutral hole
    baseline = {
        "eagle": 0.008,  # Reduced from 0.010 to control eagle inflation
        "birdie": 0.200,  # Increased from 0.190 to boost birdie rate
        "par": 0.68,  # Adjusted to maintain sum = 1.0
        "bogey": 0.095,
        "double": 0.017,
    }

    # Adjust for player skill (0-100 scale, normalize to -1 to +1 range)
    skill_factor = (skill - 50) / 50.0

    # Adjust for hole difficulty (-0.5 to +0.6 typical range)
    difficulty_factor = hole.difficulty

    # Start with baseline
    probs = baseline.copy()

    # Skill adjustments
    if skill_factor > 0:  # Better than average
        shift = skill_factor * 0.10  # Balanced to prevent elite player over-dominance
        eagle_shift = shift * 0.08  # Reduced from 0.15 to control eagle inflation
        birdie_shift = shift * 0.55  # Increased from 0.50 to boost birdie rate

        probs["eagle"] += eagle_shift
        probs["birdie"] += birdie_shift
        probs["par"] -= shift * 0.50  # Increased from 0.30 to balance weights (sum to zero)
        probs["bogey"] -= shift * 0.05
        probs["double"] -= shift * 0.05
    else:  # Worse than average
        shift = abs(skill_factor) * 0.12  # Reduced from 0.18 to be much less punitive
        probs["eagle"] -= shift * 0.08
        probs["birdie"] -= shift * 0.25  # Reduced from 0.38 to preserve more birdie opportunity
        probs["par"] -= shift * 0.10
        probs["bogey"] += shift * 0.22  # Reduced from 0.40 to control bogey inflation
        probs["double"] += shift * 0.12  # Reduced from 0.18 to control double inflation

    # Difficulty adjustments
    if difficulty_factor > 0:  # Harder hole
        shift = difficulty_factor * 0.10  # Reduced from 0.12 to soften field-wide scoring
        probs["eagle"] -= shift * 0.003
        probs["birdie"] -= shift * 0.38  # Reduced from 0.527 to reduce birdie suppression
        probs["par"] -= shift * 0.06  # Reduced from 0.07 to stop par absorption
        probs["bogey"] += shift * 0.24  # Reduced from 0.40 to control bogey inflation
        probs["double"] += shift * 0.08  # Reduced from 0.20 to control double inflation
    else:  # Easier hole
        shift = abs(difficulty_factor) * 0.07  # Reduced from 0.12 to soften field-wide scoring
        probs["eagle"] += shift * 0.003  # Reduced from 0.005 to control eagle
        probs["birdie"] += shift * 0.72  # Increased from 0.645 to boost birdie on easy holes
        probs["par"] -= shift * 0.18  # Increased from 0.10 for better balance
        probs["bogey"] -= shift * 0.35
        probs["double"] -= shift * 0.15

    # Apply player-specific trait boosts
    probs["birdie"] += birdie_boost
    probs["bogey"] -= bogey_avoid * 0.40
    probs["par"] += (bogey_avoid * 0.40) - birdie_boost

    # Aggression: increases upside and downside
    if aggression > 0:
        agg_shift = aggression * 0.04
        probs["eagle"] += agg_shift * 0.01
        probs["birdie"] += agg_shift * 0.62
        probs["par"] -= agg_shift * 0.83
        probs["bogey"] += agg_shift * 0.15
        probs["double"] += agg_shift * 0.05

    # Consistency: pulls outcomes toward par
    if consistency > 0:
        cons_shift = consistency * 0.03  # Reduced from 0.10 to prevent par over-inflation
        extreme_reduction = (probs["eagle"] + probs["double"]) * cons_shift
        probs["eagle"] *= (1 - cons_shift)
        probs["double"] *= (1 - cons_shift)
        probs["par"] += extreme_reduction

        minor_reduction = (probs["birdie"] + probs["bogey"]) * (cons_shift * 0.25)
        probs["birdie"] *= (1 - cons_shift * 0.25)
        probs["bogey"] *= (1 - cons_shift * 0.25)
        probs["par"] += minor_reduction

    # Volatility increases extremes
    vol_shift = volatility * 0.02
    probs["eagle"] += vol_shift * 0.02
    probs["double"] += vol_shift * 0.78
    probs["par"] -= vol_shift * 0.80

    # Apply safe floors BEFORE normalization to prevent probability collapse
    # These floors prevent the "floor trap" where negative values get clamped to 0.001
    # and then normalization artificially inflates par at the expense of scoring outcomes
    probs["eagle"] = max(0.002, probs["eagle"])    # Min 0.2% eagle rate
    probs["birdie"] = max(0.025, probs["birdie"])  # Min 2.5% birdie rate (critical!)
    probs["double"] = max(0.005, probs["double"])  # Min 0.5% double rate

    # Global safety net (should rarely trigger now)
    for key in probs:
        probs[key] = max(0.001, probs[key])

    # Normalize to sum to 1.0
    total = sum(probs.values())
    for key in probs:
        probs[key] /= total

    outcomes = ["eagle", "birdie", "par", "bogey", "double"]
    weights = [probs[o] for o in outcomes]

    # Sample from distribution
    result = rng.choices(outcomes, weights=weights, k=1)[0]

    # Optional debug logging for first 5 holes only
    if not hasattr(simulate_hole, "debug_count"):
        simulate_hole.debug_count = 0

    if DEBUG_HOLE_SIM and simulate_hole.debug_count < 5:
        print(f"\n=== HOLE SIMULATION DEBUG #{simulate_hole.debug_count + 1} ===")
        print(f"Player: {player_rating.get('name', 'Unknown')}")
        print(f"Hole: Par {hole.par}, Difficulty {hole.difficulty}")
        print("Probabilities passed to sampling:")
        for outcome in outcomes:
            print(f"  {outcome}: {probs[outcome]:.6f} ({probs[outcome] * 100:.4f}%)")

        score = (
            hole.par - 2 if result == "eagle"
            else hole.par - 1 if result == "birdie"
            else hole.par if result == "par"
            else hole.par + 1 if result == "bogey"
            else hole.par + 2
        )
        print(f"Sampled outcome: {result}")
        print(f"Score: {score}")

        simulate_hole.debug_count += 1

    # Track aggregate eagle probability stats
    if not hasattr(simulate_hole, "eagle_prob_sum"):
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

    return (score_map[result], result)