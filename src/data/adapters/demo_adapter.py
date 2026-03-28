"""
Demo data adapter - provides built-in sample player field.
This is for demonstration and testing purposes only.

This adapter loads from the bundled demo CSV file, providing a clean
separation between the demo data source and the generic CSV loading path.
"""
from pathlib import Path
from typing import List
from src.data.schemas import PlayerProfile
from src.data.adapters.csv_adapter import load_players_from_csv


# Default demo CSV file (bundled with repo)
DEFAULT_DEMO_CSV = Path(__file__).parent.parent.parent.parent / "data" / "demo" / "players" / "masters_2026_demo.csv"


def load_demo_field() -> List[PlayerProfile]:
    """
    Load the built-in demo player field.

    This loads from the bundled CSV file at data/demo/players/masters_2026_demo.csv.
    This ensures the demo data is consistent and repo-safe.

    Returns:
        List of PlayerProfile objects

    Raises:
        FileNotFoundError: If demo CSV is missing (should never happen in a properly cloned repo)
    """
    if not DEFAULT_DEMO_CSV.exists():
        raise FileNotFoundError(
            f"Demo CSV file not found at {DEFAULT_DEMO_CSV}. "
            "This file should be bundled with the repository."
        )

    return load_players_from_csv(str(DEFAULT_DEMO_CSV))
