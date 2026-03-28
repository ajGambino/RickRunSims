"""
Data loader - orchestrates loading player fields and tournament configurations.
"""
from typing import Tuple, Optional, List
from src.data.schemas import PlayerProfile, TournamentConfig
from src.data.adapters.demo_adapter import load_demo_field
from src.data.adapters.csv_adapter import load_players_from_csv
from src.config.tournaments.masters_2026 import get_masters_2026_config


def load_tournament_data(
    tournament_key: str,
    player_csv: Optional[str] = None,
) -> Tuple[List[PlayerProfile], TournamentConfig]:
    """
    Load player field and tournament configuration for a given tournament.

    Args:
        tournament_key: Tournament identifier (e.g., "masters_2026")
        player_csv: Optional path to CSV file with player data.
                   If None, uses built-in demo data.

    Returns:
        Tuple of (player_field, tournament_config)

    Raises:
        ValueError: If tournament_key is not recognized
        FileNotFoundError: If player_csv is specified but doesn't exist
    """
    # Map tournament keys to config loaders
    tournament_configs = {
        "masters_2026": get_masters_2026_config,
    }

    if tournament_key not in tournament_configs:
        raise ValueError(
            f"Unknown tournament: {tournament_key}. "
            f"Available: {', '.join(tournament_configs.keys())}"
        )

    # Load tournament config
    config = tournament_configs[tournament_key]()

    # Load player field from specified source
    if player_csv:
        # Load from custom CSV file
        field = load_players_from_csv(player_csv)
    else:
        # Use built-in demo data
        field = load_demo_field()

    return field, config
