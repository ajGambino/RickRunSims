"""
Masters 2026 tournament configuration.
"""
from src.data.schemas import TournamentConfig
from src.config.courses.augusta import get_augusta_course
from src.config.tournaments.generic_stroke_play import create_stroke_play_config


def get_masters_2026_config() -> TournamentConfig:
    """
    Return Masters 2026 tournament configuration.

    Tournament rules:
    - 4 rounds at Augusta National
    - Cut after round 2
    - Top 50 players and ties make the cut
    """
    augusta = get_augusta_course()

    return create_stroke_play_config(
        tournament_id="masters_2026",
        name="The Masters 2026",
        course=augusta,
        num_rounds=4,
        cut_after_round=2,
        cut_rule="top_50_and_ties",
    )
