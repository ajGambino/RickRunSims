"""
CSV data adapter - loads player data from CSV files.
Validates required fields and types, converts to PlayerProfile objects.
"""
import csv
from pathlib import Path
from typing import List
from src.data.schemas import PlayerProfile


# Expected CSV columns
REQUIRED_COLUMNS = [
    "player_id",
    "name",
    "skill_rating",
    "volatility",
]

OPTIONAL_COLUMNS = [
    "birdie_boost",
    "bogey_avoidance",
    "par3_skill",
    "par4_skill",
    "par5_skill",
    "consistency",
    "aggression",
]

# Validation ranges
SKILL_RATING_MIN = 0
SKILL_RATING_MAX = 100
VOLATILITY_MIN = 0.0
VOLATILITY_MAX = 1.0
TRAIT_MIN = -0.5
TRAIT_MAX = 0.5
PAR3_SKILL_MIN = -2
PAR3_SKILL_MAX = 2
PAR4_SKILL_MIN = -2
PAR4_SKILL_MAX = 2
PAR5_SKILL_MIN = -3
PAR5_SKILL_MAX = 3
CONSISTENCY_MIN = 0.0
CONSISTENCY_MAX = 1.0
AGGRESSION_MIN = 0.0
AGGRESSION_MAX = 1.0


class CSVValidationError(Exception):
    """Raised when CSV data fails validation."""
    pass


def load_players_from_csv(csv_path: str) -> List[PlayerProfile]:
    """
    Load player data from a CSV file.

    Args:
        csv_path: Path to CSV file with player data

    Returns:
        List of PlayerProfile objects

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        CSVValidationError: If CSV data is malformed or invalid
    """
    csv_file = Path(csv_path)

    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    players = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate header
            if reader.fieldnames is None:
                raise CSVValidationError("CSV file is empty or has no header")

            _validate_columns(reader.fieldnames)

            # Parse rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                try:
                    player = _parse_player_row(row, row_num)
                    players.append(player)
                except (ValueError, KeyError) as e:
                    raise CSVValidationError(f"Row {row_num}: {e}")

    except csv.Error as e:
        raise CSVValidationError(f"CSV parsing error: {e}")

    if not players:
        raise CSVValidationError("CSV file contains no player data")

    return players


def _validate_columns(fieldnames: List[str]) -> None:
    """Validate that required columns are present."""
    missing = set(REQUIRED_COLUMNS) - set(fieldnames)
    if missing:
        raise CSVValidationError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            f"Required: {', '.join(REQUIRED_COLUMNS)}"
        )


def _parse_optional_float(
    row: dict,
    field_name: str,
    default: float,
    min_val: float,
    max_val: float
) -> float:
    """
    Parse an optional float field from CSV row.

    Args:
        row: CSV row dictionary
        field_name: Name of field to parse
        default: Default value if field is missing or empty
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Parsed float value

    Raises:
        ValueError: If value is invalid
    """
    if field_name not in row or not row[field_name]:
        return default

    try:
        value = float(row[field_name])
    except ValueError:
        raise ValueError(f"{field_name} must be numeric, got: {row[field_name]}")

    if not (min_val <= value <= max_val):
        raise ValueError(
            f"{field_name} must be between {min_val} and {max_val}, got: {value}"
        )

    return value


def _parse_player_row(row: dict, row_num: int) -> PlayerProfile:
    """
    Parse a single CSV row into a PlayerProfile.

    Args:
        row: Dictionary of CSV row data
        row_num: Row number for error reporting

    Returns:
        PlayerProfile object

    Raises:
        ValueError: If data is invalid
    """
    # Required fields
    player_id = row["player_id"].strip()
    name = row["name"].strip()

    if not player_id:
        raise ValueError("player_id cannot be empty")
    if not name:
        raise ValueError("name cannot be empty")

    # Parse and validate numeric fields
    try:
        skill_rating = float(row["skill_rating"])
    except ValueError:
        raise ValueError(f"skill_rating must be numeric, got: {row['skill_rating']}")

    if not (SKILL_RATING_MIN <= skill_rating <= SKILL_RATING_MAX):
        raise ValueError(
            f"skill_rating must be between {SKILL_RATING_MIN} and {SKILL_RATING_MAX}, "
            f"got: {skill_rating}"
        )

    try:
        volatility = float(row["volatility"])
    except ValueError:
        raise ValueError(f"volatility must be numeric, got: {row['volatility']}")

    if not (VOLATILITY_MIN <= volatility <= VOLATILITY_MAX):
        raise ValueError(
            f"volatility must be between {VOLATILITY_MIN} and {VOLATILITY_MAX}, "
            f"got: {volatility}"
        )

    # Optional fields with defaults
    birdie_boost = 0.0
    if "birdie_boost" in row and row["birdie_boost"]:
        try:
            birdie_boost = float(row["birdie_boost"])
        except ValueError:
            raise ValueError(f"birdie_boost must be numeric, got: {row['birdie_boost']}")

        if not (TRAIT_MIN <= birdie_boost <= TRAIT_MAX):
            raise ValueError(
                f"birdie_boost must be between {TRAIT_MIN} and {TRAIT_MAX}, "
                f"got: {birdie_boost}"
            )

    bogey_avoidance = 0.0
    if "bogey_avoidance" in row and row["bogey_avoidance"]:
        try:
            bogey_avoidance = float(row["bogey_avoidance"])
        except ValueError:
            raise ValueError(f"bogey_avoidance must be numeric, got: {row['bogey_avoidance']}")

        if not (TRAIT_MIN <= bogey_avoidance <= TRAIT_MAX):
            raise ValueError(
                f"bogey_avoidance must be between {TRAIT_MIN} and {TRAIT_MAX}, "
                f"got: {bogey_avoidance}"
            )

    # Par-specific skill modifiers (tightened ranges for calibration)
    par3_skill = _parse_optional_float(row, "par3_skill", 0.0, PAR3_SKILL_MIN, PAR3_SKILL_MAX)
    par4_skill = _parse_optional_float(row, "par4_skill", 0.0, PAR4_SKILL_MIN, PAR4_SKILL_MAX)
    par5_skill = _parse_optional_float(row, "par5_skill", 0.0, PAR5_SKILL_MIN, PAR5_SKILL_MAX)

    # Play-style traits
    consistency = _parse_optional_float(row, "consistency", 0.0, CONSISTENCY_MIN, CONSISTENCY_MAX)
    aggression = _parse_optional_float(row, "aggression", 0.0, AGGRESSION_MIN, AGGRESSION_MAX)

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
