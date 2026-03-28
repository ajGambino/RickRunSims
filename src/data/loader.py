"""
Data loader - orchestrates loading player fields and tournament configurations.
"""
from typing import Tuple
from src.data.schemas import PlayerProfile, TournamentConfig
from src.data.adapters.demo_adapter import load_demo_field
from src.config.tournaments.masters_2026 import get_masters_2026_config


def load_tournament_data(tournament_key: str) -> Tuple[list[PlayerProfile], TournamentConfig]:
    """
    Load player field and tournament configuration for a given tournament.

    Args:
        tournament_key: Tournament identifier (e.g., "masters_2026")

    Returns:
        Tuple of (player_field, tournament_config)

    Raises:
        ValueError: If tournament_key is not recognized
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

    # For now, always use demo field
    # TODO: Add support for loading different fields per tournament
    # TODO: Add support for CSV adapter and Rick private adapter
    field = load_demo_field()

    return field, config
