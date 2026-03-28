"""
Generic stroke play tournament configuration helper.
"""
from typing import Optional
from src.data.schemas import TournamentConfig, CourseProfile


def create_stroke_play_config(
    tournament_id: str,
    name: str,
    course: CourseProfile,
    num_rounds: int = 4,
    cut_after_round: Optional[int] = None,
    cut_rule: Optional[str] = None,
) -> TournamentConfig:
    """
    Create a stroke play tournament configuration.

    Args:
        tournament_id: Unique identifier for the tournament
        name: Display name
        course: Course to play on
        num_rounds: Number of rounds (typically 4)
        cut_after_round: Round after which to apply cut (e.g., 2)
        cut_rule: Cut rule (e.g., "top_50_and_ties")

    Returns:
        TournamentConfig object
    """
    return TournamentConfig(
        tournament_id=tournament_id,
        name=name,
        course=course,
        num_rounds=num_rounds,
        cut_after_round=cut_after_round,
        cut_rule=cut_rule,
    )
