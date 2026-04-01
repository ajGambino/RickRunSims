"""
Tournament-level simulation engine.
Simulates a complete tournament with multiple rounds and optional cut.
"""
import random
from typing import List
from src.data.schemas import TournamentConfig
from src.models.results import PlayerTournamentResult, TournamentSimResult
from src.sim.round_engine import simulate_round
from src.sim.cut_engine import apply_cut


def simulate_tournament(
    player_ratings: List[dict],
    config: TournamentConfig,
    rng: random.Random
) -> TournamentSimResult:
    """
    Simulate one complete tournament.

    Args:
        player_ratings: List of player rating dicts
        config: TournamentConfig
        rng: Random number generator

    Returns:
        TournamentSimResult with complete results and leaderboard
    """
    # Initialize player tournament results
    player_results = {
        pr["player_id"]: PlayerTournamentResult(
            player_id=pr["player_id"],
            player_name=pr["player_name"],
            rounds=[],
            made_cut=True,  # Assume all make cut initially
        )
        for pr in player_ratings
    }

    # Track who is still playing
    active_player_ids = set(pr["player_id"] for pr in player_ratings)

    # Simulate each round
    for round_num in range(1, config.num_rounds + 1):
        # Get active players for this round
        active_ratings = [pr for pr in player_ratings if pr["player_id"] in active_player_ids]

        # Simulate the round
        round_results = simulate_round(active_ratings, config.course, round_num, rng)

        # Store results
        for rr in round_results:
            player_results[rr.player_id].rounds.append(rr)

        # Apply cut if this is the cut round
        if config.cut_after_round == round_num and config.cut_rule is not None:
            # Convert player_results dict to list for cut engine
            results_list = list(player_results.values())
            made_cut_ids = apply_cut(results_list, config.cut_rule)

            # Update made_cut status and active players
            for player_id in player_results:
                if player_id not in made_cut_ids:
                    player_results[player_id].made_cut = False

            active_player_ids = made_cut_ids

    # Determine final standings
    final_results = list(player_results.values())
    final_results.sort(key=lambda p: p.total_to_par)

    # Assign finish positions
    position = 1
    prev_score = None
    tied_players = []

    for i, player in enumerate(final_results):
        current_score = player.total_to_par

        if prev_score is not None and current_score != prev_score:
            # Assign position to tied players
            position = i + 1

        player.finish_position = position
        prev_score = current_score

    # Determine winner (handle ties with random selection for now)
    # TODO: Implement proper playoff logic
    winners = [p for p in final_results if p.finish_position == 1]
    if len(winners) > 1:
        # Random tiebreaker (placeholder for playoff)
        winner = rng.choice(winners)
    else:
        winner = winners[0]

    return TournamentSimResult(
        tournament_id=config.tournament_id,
        player_results=final_results,
        winner_id=winner.player_id,
        winner_name=winner.player_name,
        winning_score=winner.total_to_par,
    )
