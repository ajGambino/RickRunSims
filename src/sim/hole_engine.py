"""
Hole-level simulation engine.
Simulates a single hole for a single player using rule-based scoring model.
"""
import random
from src.data.schemas import HoleProfile

DEBUG_HOLE_SIM = False
DEBUG_TAIL_CALIBRATION = True  # Diagnostic for bogey/double+ distribution


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
        "par": 0.640,  # Reduced from 0.68 to free up mass for bad outcomes
        "bogey": 0.09,  # Increased from 0.095 to strengthen baseline error rate
        "double": 0.055,  # Increased from 0.017 to strengthen tail baseline
    }

    # Adjust for player skill (0-100 scale, normalize to -1 to +1 range)
    skill_factor = (skill - 50) / 65.0

    # Adjust for hole difficulty (-0.5 to +0.6 typical range)
    difficulty_factor = hole.difficulty

    # Start with baseline
    probs = baseline.copy()

    # Initialize diagnostics tracking
    if not hasattr(simulate_hole, "diag_counters"):
        simulate_hole.diag_counters = {
            "total_holes": 0,
            "below_avg_skill_fires": 0,
            "harder_hole_fires": 0,
            "skill_shift_sum": 0.0,
            "diff_shift_sum": 0.0,
            "bogey_before_skill": [],
            "double_before_skill": [],
            "bogey_after_skill": [],
            "double_after_skill": [],
            "bogey_before_diff": [],
            "double_before_diff": [],
            "bogey_after_diff": [],
            "double_after_diff": [],
            "bogey_before_norm": [],
            "double_before_norm": [],
            "bogey_after_norm": [],
            "double_after_norm": [],
        }

    simulate_hole.diag_counters["total_holes"] += 1

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
        simulate_hole.diag_counters["below_avg_skill_fires"] += 1
        simulate_hole.diag_counters["bogey_before_skill"].append(probs["bogey"])
        simulate_hole.diag_counters["double_before_skill"].append(probs["double"])

        shift = abs(skill_factor) * 0.12  # Reduced from 0.18 to be much less punitive
        simulate_hole.diag_counters["skill_shift_sum"] += shift

        probs["eagle"] -= shift * 0.08
        probs["birdie"] -= shift * 0.25  # Reduced from 0.38 to preserve more birdie opportunity
        probs["par"] -= shift * 0.10
        probs["bogey"] += shift * 0.14  # Reduced from 0.22 to shift mass to double+
        probs["double"] += shift * 0.20  # Increased from 0.12 to capture tail risk

        simulate_hole.diag_counters["bogey_after_skill"].append(probs["bogey"])
        simulate_hole.diag_counters["double_after_skill"].append(probs["double"])

    # Difficulty adjustments
    if difficulty_factor > 0:  # Harder hole
        simulate_hole.diag_counters["harder_hole_fires"] += 1
        simulate_hole.diag_counters["bogey_before_diff"].append(probs["bogey"])
        simulate_hole.diag_counters["double_before_diff"].append(probs["double"])

        shift = difficulty_factor * 0.10  # Reduced from 0.12 to soften field-wide scoring
        simulate_hole.diag_counters["diff_shift_sum"] += shift

        probs["eagle"] -= shift * 0.003
        probs["birdie"] -= shift * 0.38  # Reduced from 0.527 to reduce birdie suppression
        probs["par"] -= shift * 0.06  # Reduced from 0.07 to stop par absorption
        probs["bogey"] += shift * 0.16  # Reduced from 0.24 to shift mass to double+
        probs["double"] += shift * 0.16  # Increased from 0.08 to strengthen tail on hard holes

        simulate_hole.diag_counters["bogey_after_diff"].append(probs["bogey"])
        simulate_hole.diag_counters["double_after_diff"].append(probs["double"])
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

    # Capture pre-normalization state
    simulate_hole.diag_counters["bogey_before_norm"].append(probs["bogey"])
    simulate_hole.diag_counters["double_before_norm"].append(probs["double"])

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

    # Capture post-normalization state
    simulate_hole.diag_counters["bogey_after_norm"].append(probs["bogey"])
    simulate_hole.diag_counters["double_after_norm"].append(probs["double"])

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


def print_tail_calibration_diagnostics():
    """Print diagnostic report for bogey/double+ redistribution analysis."""
    if not hasattr(simulate_hole, "diag_counters"):
        print("No diagnostic data collected.")
        return

    dc = simulate_hole.diag_counters
    total = dc["total_holes"]

    if total == 0:
        print("No holes simulated yet.")
        return

    print("\n" + "=" * 70)
    print("TAIL CALIBRATION DIAGNOSTICS")
    print("=" * 70)

    # Branch activation rates
    print(f"\n1. BRANCH ACTIVATION")
    print(f"   Total holes simulated: {total:,}")
    print(f"   Below-average skill fires: {dc['below_avg_skill_fires']:,} ({100 * dc['below_avg_skill_fires'] / total:.1f}%)")
    print(f"   Harder hole fires: {dc['harder_hole_fires']:,} ({100 * dc['harder_hole_fires'] / total:.1f}%)")

    # Shift magnitudes
    print(f"\n2. SHIFT MAGNITUDES")
    if dc["below_avg_skill_fires"] > 0:
        avg_skill_shift = dc["skill_shift_sum"] / dc["below_avg_skill_fires"]
        print(f"   Avg skill shift (when fired): {avg_skill_shift:.6f}")
    else:
        print(f"   Avg skill shift: N/A (never fired)")

    if dc["harder_hole_fires"] > 0:
        avg_diff_shift = dc["diff_shift_sum"] / dc["harder_hole_fires"]
        print(f"   Avg difficulty shift (when fired): {avg_diff_shift:.6f}")
    else:
        print(f"   Avg difficulty shift: N/A (never fired)")

    # Probability changes in skill adjustment block
    if dc["bogey_before_skill"]:
        print(f"\n3. SKILL ADJUSTMENT BLOCK (below-average players)")
        avg_bogey_before = sum(dc["bogey_before_skill"]) / len(dc["bogey_before_skill"])
        avg_bogey_after = sum(dc["bogey_after_skill"]) / len(dc["bogey_after_skill"])
        avg_double_before = sum(dc["double_before_skill"]) / len(dc["double_before_skill"])
        avg_double_after = sum(dc["double_after_skill"]) / len(dc["double_after_skill"])

        print(f"   Bogey:   {avg_bogey_before:.6f} → {avg_bogey_after:.6f} (Δ = {avg_bogey_after - avg_bogey_before:+.6f})")
        print(f"   Double+: {avg_double_before:.6f} → {avg_double_after:.6f} (Δ = {avg_double_after - avg_double_before:+.6f})")

    # Probability changes in difficulty adjustment block
    if dc["bogey_before_diff"]:
        print(f"\n4. DIFFICULTY ADJUSTMENT BLOCK (harder holes)")
        avg_bogey_before = sum(dc["bogey_before_diff"]) / len(dc["bogey_before_diff"])
        avg_bogey_after = sum(dc["bogey_after_diff"]) / len(dc["bogey_after_diff"])
        avg_double_before = sum(dc["double_before_diff"]) / len(dc["double_before_diff"])
        avg_double_after = sum(dc["double_after_diff"]) / len(dc["double_after_diff"])

        print(f"   Bogey:   {avg_bogey_before:.6f} → {avg_bogey_after:.6f} (Δ = {avg_bogey_after - avg_bogey_before:+.6f})")
        print(f"   Double+: {avg_double_before:.6f} → {avg_double_after:.6f} (Δ = {avg_double_after - avg_double_before:+.6f})")

    # Normalization impact
    if dc["bogey_before_norm"]:
        print(f"\n5. NORMALIZATION IMPACT (all holes)")
        avg_bogey_before = sum(dc["bogey_before_norm"]) / len(dc["bogey_before_norm"])
        avg_bogey_after = sum(dc["bogey_after_norm"]) / len(dc["bogey_after_norm"])
        avg_double_before = sum(dc["double_before_norm"]) / len(dc["double_before_norm"])
        avg_double_after = sum(dc["double_after_norm"]) / len(dc["double_after_norm"])

        print(f"   Bogey:   {avg_bogey_before:.6f} → {avg_bogey_after:.6f} (Δ = {avg_bogey_after - avg_bogey_before:+.6f})")
        print(f"   Double+: {avg_double_before:.6f} → {avg_double_after:.6f} (Δ = {avg_double_after - avg_double_before:+.6f})")

        bogey_shrinkage = (avg_bogey_after - avg_bogey_before) / avg_bogey_before * 100 if avg_bogey_before > 0 else 0
        double_shrinkage = (avg_double_after - avg_double_before) / avg_double_before * 100 if avg_double_before > 0 else 0

        print(f"   Bogey shrinkage: {bogey_shrinkage:+.2f}%")
        print(f"   Double+ shrinkage: {double_shrinkage:+.2f}%")

    print("\n" + "=" * 70 + "\n")