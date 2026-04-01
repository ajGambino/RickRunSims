"""
Round-level simulation engine.
Simulates one full round (18 holes) for all players in the field.
"""
import random
from typing import List
from src.data.schemas import CourseProfile
from src.models.results import PlayerRoundResult
from src.sim.hole_engine import simulate_hole


def simulate_round(
    player_ratings: List[dict],
    course: CourseProfile,
    round_number: int,
    rng: random.Random
) -> List[PlayerRoundResult]:
    """
    Simulate one round for all players.

    Args:
        player_ratings: List of player rating dictionaries
        course: CourseProfile with holes
        round_number: Which round this is (1-4)
        rng: Random number generator

    Returns:
        List of PlayerRoundResult objects
    """
    results = []

    for player_rating in player_ratings:
        hole_scores = []
        hole_outcomes = []

        # Simulate each hole
        for hole in course.holes:
            score, outcome = simulate_hole(player_rating, hole, rng)
            hole_scores.append(score)
            hole_outcomes.append(outcome)

            # Create round result
        total_score = sum(hole_scores)
        round_par = course.total_par
        score_to_par = total_score - round_par

        round_result = PlayerRoundResult(
            player_id=player_rating["player_id"],
            player_name=player_rating["player_name"],
            round_number=round_number,
            hole_scores=hole_scores,
            hole_outcomes=hole_outcomes,
            _score_to_par=score_to_par
        )

        results.append(round_result)

    return results
