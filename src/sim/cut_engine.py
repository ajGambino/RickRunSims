"""
Cut engine - determines which players make the cut.
"""
from typing import List, Set
from src.models.results import PlayerTournamentResult


def apply_cut(
    player_results: List[PlayerTournamentResult],
    cut_rule: str,
) -> Set[str]:
    """
    Apply tournament cut and return set of player IDs who made the cut.

    Args:
        player_results: Current player tournament results
        cut_rule: Cut rule to apply (e.g., "top_50_and_ties")

    Returns:
        Set of player_ids who made the cut
    """
    if cut_rule == "top_50_and_ties":
        return _apply_top_n_and_ties(player_results, n=50)
    else:
        raise ValueError(f"Unknown cut rule: {cut_rule}")


def _apply_top_n_and_ties(
    player_results: List[PlayerTournamentResult],
    n: int
) -> Set[str]:
    """
    Apply top N and ties cut rule.

    All players tied at the Nth position score also make the cut.

    Args:
        player_results: Current player tournament results
        n: Number of players to keep (before considering ties)

    Returns:
        Set of player_ids who made the cut
    """
    # Sort by total score (lower is better)
    sorted_players = sorted(player_results, key=lambda p: p.total_to_par)

    # Find the cut line score (score of the nth player)
    if len(sorted_players) <= n:
        # Everyone makes the cut if field is smaller than cut size
        return {p.player_id for p in sorted_players}

    cut_line_score = sorted_players[n - 1].total_to_par

    # Include all players at or better than cut line (handles ties)
    made_cut = set()
    for player in sorted_players:
        if player.total_to_par <= cut_line_score:
            made_cut.add(player.player_id)
        else:
            break

    return made_cut
