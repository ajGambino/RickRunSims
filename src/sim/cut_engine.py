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
    # Compute cut score based only on first 2 rounds (36 holes)
    def cut_score(p: PlayerTournamentResult) -> int:
        return sum(r.score_to_par for r in p.rounds[:2])
    

    # Sort by cut score (lower is better)
    sorted_players = sorted(player_results, key=cut_score)
    
    # Find the cut line score (score of the nth player)
    if len(sorted_players) <= n:
        # Everyone makes the cut if field is smaller than cut size
        return {p.player_id for p in sorted_players}

    cut_line_score = cut_score(sorted_players[n - 1])

    # Include all players at or better than cut line (handles ties)
    made_cut = set()
    for player in sorted_players:
        if cut_score(player) <= cut_line_score:
            made_cut.add(player.player_id)
        else:
            break
            
    return made_cut
