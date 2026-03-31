"""
Data loader - orchestrates loading player fields and tournament configurations.
"""
from typing import Tuple, Optional, List
from src.data.schemas import PlayerProfile, TournamentConfig
from src.data.adapters.demo_adapter import load_demo_field
from src.data.adapters.csv_adapter import load_players_from_csv
from data.adapters.private_adapter import load_players_from_raw
from src.config.tournaments.masters_2026 import get_masters_2026_config


def load_tournament_data(
    tournament_key: str,
    player_csv: Optional[str] = None,
    raw_player_csv: Optional[str] = None,
    raw_round_csv: Optional[str] = None,
) -> Tuple[List[PlayerProfile], TournamentConfig]:
    """
    Load player field and tournament configuration for a given tournament.

    Args:
        tournament_key: Tournament identifier (e.g., "masters_2026")
        player_csv: Optional path to sim-ready CSV file with player data.
                   If None, uses built-in demo data.
        raw_player_csv: Optional path to raw player statistics CSV.
                       If provided, uses private data pipeline.
        raw_round_csv: Optional path to raw round-by-round CSV.
                      Used with raw_player_csv for volatility calculation.

    Returns:
        Tuple of (player_field, tournament_config)

    Raises:
        ValueError: If tournament_key is not recognized
        FileNotFoundError: If specified CSV files don't exist
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

    # Load player field from specified source (priority order)
    if raw_player_csv:
        # Load from raw private data (highest priority)
        print(f"Loading from raw player data: {raw_player_csv}")
        if raw_round_csv:
            print(f"Using round data for volatility: {raw_round_csv}")
        field = load_players_from_raw(raw_player_csv, raw_round_csv)
    elif player_csv:
        # Load from sim-ready CSV file
        field = load_players_from_csv(player_csv)
    else:
        # Use built-in demo data
        field = load_demo_field()

    return field, config
