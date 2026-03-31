"""
Private raw data adapter - loads player data from private/proprietary raw golf statistics.

This adapter transforms raw strokes-gained and performance statistics into
simulation-ready PlayerProfile objects.

All file paths must be passed as parameters
"""
import csv
import math
from pathlib import Path
from typing import List, Optional, Dict, Sequence
from collections import defaultdict
from src.data.schemas import PlayerProfile


# ============================================================================
# Configuration & Constants
# ============================================================================

# Sample size thresholds for shrinkage
MIN_ROUNDS_FULL_WEIGHT = 50  # Rounds needed for full weight (no shrinkage)
MIN_ROUNDS_PARTIAL = 10  # Minimum rounds to use player data at all

# Skill rating normalization (map SG Total to 0-100 scale)
# PGA Tour average is ~0.0 SG Total
# Elite players: +2 to +3 SG Total
# Top players: +1 to +2 SG Total
# Average tour players: -0.5 to +0.5 SG Total
SKILL_RATING_CENTER = 50.0  # Maps to 0.0 SG Total
SKILL_RATING_SCALE = 20.0  # 1.0 SG Total = 20 points

# Par-specific skill compression (raw SG to -2/+2 range)
PAR_SKILL_SCALE = 1.5  # 1.0 SG = 1.5 skill points (compressed from wider raw range)
PAR3_MAX = 2.0
PAR4_MAX = 2.0
PAR5_MAX = 3.0

# Birdie boost & bogey avoid modifiers (modest effects)
BIRDIE_BOOST_SCALE = 0.10  # Max effect from raw inputs
BOGEY_AVOID_SCALE = 0.10  # Max effect from raw inputs

# Volatility defaults
DEFAULT_VOLATILITY = 0.25
VOLATILITY_MIN = 0.15
VOLATILITY_MAX = 0.50


# ============================================================================
# Raw Data Loading
# ============================================================================

def load_players_from_raw(
    player_csv_path: str,
    round_csv_path: Optional[str] = None,
) -> List[PlayerProfile]:
    """
    Load player profiles from raw golf statistics CSV files.

    Args:
        player_csv_path: Path to comprehensive player stats CSV
        round_csv_path: Optional path to round-by-round performance CSV

    Returns:
        List of PlayerProfile objects ready for simulation

    Raises:
        FileNotFoundError: If required CSV files don't exist
        ValueError: If required columns are missing
    """
    player_file = Path(player_csv_path)
    if not player_file.exists():
        raise FileNotFoundError(f"Player CSV not found: {player_csv_path}")

    # Load round-level data if provided (for volatility calculation)
    player_round_data = None
    if round_csv_path:
        round_file = Path(round_csv_path)
        if not round_file.exists():
            raise FileNotFoundError(f"Round CSV not found: {round_csv_path}")
        player_round_data = _load_round_data(round_csv_path)

    # Load and transform player data
    players = []
    with open(player_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Validate required columns
        _validate_required_columns(reader.fieldnames)

        for row in reader:
            # Skip rows with missing critical data
            if not row.get('player_id') or not row.get('name'):
                continue

            # Skip players with insufficient sample size
            rounds = _safe_float(row.get('rounds'), 0.0)
            sg_rounds = _safe_float(row.get('sg_rounds'), rounds if rounds is not None else 0.0)
            if sg_rounds is None or sg_rounds < MIN_ROUNDS_PARTIAL:
                continue

            # Build player profile from raw stats
            player = _build_player_profile(row, player_round_data)
            players.append(player)

    if not players:
        raise ValueError("No valid players found in CSV (check sample sizes)")

    return players


def _load_round_data(round_csv_path: str) -> Dict[str, List[float]]:
    """
    Load round-by-round TOT (Total strokes gained) for volatility calculation.

    Returns:
        Dict mapping player name -> list of TOT values
    """
    player_rounds = defaultdict(list)

    with open(round_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            player_name = row.get('Player', '').strip()
            tot = _safe_float(row.get('TOT'))

            if player_name and tot is not None:
                player_rounds[player_name].append(tot)

    return dict(player_rounds)


def _validate_required_columns(fieldnames: Optional[Sequence[str]]) -> None:
    """Validate that required columns are present in the CSV."""
    if not fieldnames:
        raise ValueError("CSV file is empty or has no header")

    required = ['player_id', 'name', 'sg_tot']
    missing = set(required) - set(fieldnames)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            f"Required: {', '.join(required)}"
        )


# ============================================================================
# Feature Transformation Functions
# ============================================================================

def _build_player_profile(
    row: Dict[str, str],
    round_data: Optional[Dict[str, List[float]]]
) -> PlayerProfile:
    """
    Transform raw golf statistics into a PlayerProfile.

    Mapping strategy:
    - skill_rating: Derived from sg_tot with optional w_sg_tot and recent form blend
    - par X_skill: Derived from sg_par_X with compression
    - birdie_boost: Proxy from bob/bobg + sg_app + sg_putt + sg_par_5
    - bogey_avoidance: Derived from bogey_avoid + scrambling
    - volatility: Computed from round-level variance or fallback proxy
    - consistency: Inverse of volatility
    - aggression: Neutral default for now
    """
    player_id = row['player_id'].strip()
    name = row['name'].strip()

    # Sample size for shrinkage
    rounds = _safe_float(row.get('rounds'), 0.0)
    sg_rounds = _safe_float(row.get('sg_rounds'), rounds if rounds is not None else 0.0)
    shrinkage_weight = _calculate_shrinkage_weight(sg_rounds if sg_rounds is not None else 0.0)

    # Build skill rating
    skill_rating = _derive_skill_rating(row, shrinkage_weight)

    # Build par-specific skills
    par3_skill = _derive_par_skill(row, 'sg_par_3', shrinkage_weight, PAR3_MAX)
    par4_skill = _derive_par_skill(row, 'sg_par_4', shrinkage_weight, PAR4_MAX)
    par5_skill = _derive_par_skill(row, 'sg_par_5', shrinkage_weight, PAR5_MAX)

    # Build birdie boost
    birdie_boost = _derive_birdie_boost(row, shrinkage_weight)

    # Build bogey avoidance
    bogey_avoidance = _derive_bogey_avoidance(row, shrinkage_weight)

    # Build volatility
    volatility = _derive_volatility(name, round_data, row, shrinkage_weight)

    # Consistency is inverse of volatility
    consistency = _derive_consistency(volatility)

    # Aggression: neutral default for now
    aggression = 0.0

    return PlayerProfile(
        player_id=player_id,
        name=name,
        skill_rating=skill_rating,
        volatility=volatility,
        birdie_boost=birdie_boost,
        bogey_avoidance=bogey_avoidance,
        par3_skill=par3_skill,
        par4_skill=par4_skill,
        par5_skill=par5_skill,
        consistency=consistency,
        aggression=aggression,
    )


def _derive_skill_rating(row: Dict[str, str], shrinkage: float) -> float:
    """
    Derive skill_rating from sg_tot with optional blending.

    Formula:
    1. Base: sg_tot mapped to 0-100 scale
    2. Optional blend with w_sg_tot if available
    3. Optional light recent-form adjustment
    4. Apply shrinkage to pull toward field mean
    """
    sg_tot = _safe_float(row.get('sg_tot'), 0.0) or 0.0
    w_sg_tot = _safe_float(row.get('w_sg_tot'))

    # Start with sg_tot
    base_sg = sg_tot

    # Optionally blend with weighted SG if available (70/30 split)
    if w_sg_tot is not None:
        base_sg = 0.7 * sg_tot + 0.3 * w_sg_tot  # type: ignore

    # Optionally add light recent-form adjustment (app/ott/putt L12)
    recent_form_adj = 0.0
    sg_app_l12 = _safe_float(row.get('sg_app_l_12'), 0.0)
    sg_ott_l12 = _safe_float(row.get('sg_ott_l_12'), 0.0)
    sg_putt_l12 = _safe_float(row.get('sg_putt_l_12'), 0.0)

    if all(x is not None for x in [sg_app_l12, sg_ott_l12, sg_putt_l12]):
        recent_form = (sg_app_l12 or 0.0) + (sg_ott_l12 or 0.0) + (sg_putt_l12 or 0.0)
        # These have defaults so they won't be None
        sg_app_val = _safe_float(row.get('sg_app'), 0.0) or 0.0
        sg_ott_val = _safe_float(row.get('sg_ott'), 0.0) or 0.0
        sg_putt_val = _safe_float(row.get('sg_putt'), 0.0) or 0.0
        season_form = sg_app_val + sg_ott_val + sg_putt_val
        recent_form_adj = 0.10 * (recent_form - season_form)  # 10% weight on delta

    # Combined SG
    final_sg = base_sg + recent_form_adj

    # Apply shrinkage toward 0.0 (tour average)
    final_sg = shrinkage * final_sg + (1 - shrinkage) * 0.0

    # Map to 0-100 scale
    skill_rating = SKILL_RATING_CENTER + final_sg * SKILL_RATING_SCALE

    # Clamp to valid range
    return max(0.0, min(100.0, skill_rating))


def _derive_par_skill(
    row: Dict[str, str],
    column_name: str,
    shrinkage: float,
    max_val: float
) -> float:
    """
    Derive par-specific skill from sg_par_X column.

    Formula:
    1. Get sg_par_X value
    2. Apply shrinkage toward 0.0
    3. Scale and compress to fit range
    4. Clamp to [-max_val, +max_val]
    """
    sg_par = _safe_float(row.get(column_name), 0.0) or 0.0

    # Apply shrinkage
    sg_par = shrinkage * sg_par + (1 - shrinkage) * 0.0

    # Scale and compress
    par_skill = sg_par * PAR_SKILL_SCALE

    # Clamp to range
    return max(-max_val, min(max_val, par_skill))


def _derive_birdie_boost(row: Dict[str, str], shrinkage: float) -> float:
    """
    Derive birdie_boost from birdie opportunities and scoring ability.

    Formula:
    Transparent proxy using:
    - bob or bobg (birdies or better per game)
    - sg_app (approach skill)
    - sg_putt (putting skill)
    - sg_par_5 (scoring on par 5s)
    - gir (greens in regulation, optional)

    Keep effect modest (max ~0.10)
    """
    # Get components
    bob = _safe_float(row.get('bob'))
    bobg = _safe_float(row.get('bobg'))
    sg_app = _safe_float(row.get('sg_app'), 0.0) or 0.0
    sg_putt = _safe_float(row.get('sg_putt'), 0.0) or 0.0
    sg_par_5 = _safe_float(row.get('sg_par_5'), 0.0) or 0.0
    gir = _safe_float(row.get('gir'))

    # Build composite score
    score = 0.0

    # Bob/bobg contribution (normalize: ~4.0 bobg is elite)
    if bobg is not None:
        score += (bobg - 3.5) * 0.3  # Center at 3.5, scale by 0.3
    elif bob is not None:
        score += (bob / 18.0 - 3.5) * 0.3  # Convert bob to per-round equivalent

    # SG contributions
    score += sg_app * 0.3
    score += sg_putt * 0.2
    score += sg_par_5 * 0.2

    # GIR contribution (optional, normalize: ~70% is tour average)
    if gir is not None:
        score += (gir - 70.0) * 0.01

    # Apply shrinkage
    score = shrinkage * score + (1 - shrinkage) * 0.0

    # Scale and clamp
    birdie_boost = score * BIRDIE_BOOST_SCALE
    return max(-0.15, min(0.15, birdie_boost))


def _derive_bogey_avoidance(row: Dict[str, str], shrinkage: float) -> float:
    """
    Derive bogey_avoidance from bogey avoidance stats and scrambling.

    Formula:
    - bogey_avoid (primary driver)
    - scrambling (recovery ability)

    Keep effect modest (max ~0.10)
    """
    bogey_avoid = _safe_float(row.get('bogey_avoid'), 0.0) or 0.0
    scrambling = _safe_float(row.get('scrambling'))

    # Build score
    score = 0.0

    # Bogey avoid contribution (normalize: ~1.0 is average)
    score += (bogey_avoid - 1.0) * 0.6

    # Scrambling contribution (normalize: ~60% is tour average)
    if scrambling is not None:
        score += (scrambling - 60.0) * 0.02

    # Apply shrinkage
    score = shrinkage * score + (1 - shrinkage) * 0.0

    # Scale and clamp
    bogey_avoid_val = score * BOGEY_AVOID_SCALE
    return max(-0.15, min(0.15, bogey_avoid_val))


def _derive_volatility(
    name: str,
    round_data: Optional[Dict[str, List[float]]],
    row: Dict[str, str],
    shrinkage: float
) -> float:
    """
    Derive volatility from round-level variance or fallback proxy.

    Strategy:
    1. If round_data is provided, compute stdev of TOT values
    2. Otherwise, use fallback proxy (based on general stats)
    3. Apply shrinkage toward default
    4. Clamp to reasonable range
    """
    if round_data and name in round_data:
        tot_values = round_data[name]
        if len(tot_values) >= 5:  # Need at least 5 rounds
            stdev = _compute_stdev(tot_values)
            # Map stdev to volatility (typical stdev: 1.5-3.0)
            # 1.5 stdev -> 0.15 volatility
            # 2.5 stdev -> 0.25 volatility
            # 3.5 stdev -> 0.35 volatility
            volatility = 0.10 * stdev
            volatility = max(VOLATILITY_MIN, min(VOLATILITY_MAX, volatility))
            return volatility

    # Fallback proxy: use variance indicators from player stats
    # Higher skill variance indicators -> higher volatility
    fallback = DEFAULT_VOLATILITY

    # If we have sg_app and sg_ott, use their magnitude as variance proxy
    sg_app = _safe_float(row.get('sg_app'), 0.0) or 0.0
    sg_ott = _safe_float(row.get('sg_ott'), 0.0) or 0.0
    sg_putt = _safe_float(row.get('sg_putt'), 0.0) or 0.0

    # Players with extreme strengths/weaknesses tend to be more volatile
    skill_spread = abs(sg_app - sg_ott) + abs(sg_putt - sg_app)
    volatility_adj = skill_spread * 0.02  # Small adjustment based on imbalance

    fallback = DEFAULT_VOLATILITY + volatility_adj
    fallback = max(VOLATILITY_MIN, min(VOLATILITY_MAX, fallback))

    # Apply shrinkage toward default
    final_volatility = shrinkage * fallback + (1 - shrinkage) * DEFAULT_VOLATILITY

    return max(VOLATILITY_MIN, min(VOLATILITY_MAX, final_volatility))


def _derive_consistency(volatility: float) -> float:
    """
    Derive consistency as inverse of volatility.

    Lower volatility -> higher consistency
    Map volatility [0.15, 0.50] to consistency [0.7, 0.0]
    """
    # Normalize volatility to 0-1 scale
    vol_normalized = (volatility - VOLATILITY_MIN) / (VOLATILITY_MAX - VOLATILITY_MIN)

    # Invert: high volatility = low consistency
    consistency = 1.0 - vol_normalized

    # Scale to meaningful range (0.0 to 0.7, where 0.7 is very consistent)
    consistency = consistency * 0.7

    return max(0.0, min(1.0, consistency))


# ============================================================================
# Helper Functions
# ============================================================================

def _calculate_shrinkage_weight(rounds: float) -> float:
    """
    Calculate shrinkage weight based on sample size.

    More rounds -> higher weight (less shrinkage toward mean)

    Returns:
        Float between 0.0 and 1.0
        1.0 = full weight (no shrinkage)
        0.0 = no weight (full shrinkage to mean)
    """
    if rounds >= MIN_ROUNDS_FULL_WEIGHT:
        return 1.0
    elif rounds <= MIN_ROUNDS_PARTIAL:
        return 0.3  # Minimum weight
    else:
        # Linear interpolation between partial and full
        return 0.3 + 0.7 * (rounds - MIN_ROUNDS_PARTIAL) / (MIN_ROUNDS_FULL_WEIGHT - MIN_ROUNDS_PARTIAL)


def _safe_float(value: Optional[str], default: Optional[float] = None) -> Optional[float]:
    """
    Safely convert string to float, returning default if conversion fails.

    Returns None if value is missing/empty and default is None.
    """
    if value is None or value == '':
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _compute_stdev(values: List[float]) -> float:
    """Compute standard deviation of a list of values."""
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)
