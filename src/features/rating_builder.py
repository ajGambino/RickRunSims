"""
Rating builder - converts player profiles into simulation-ready ratings.
Lightweight feature engineering for v1.
"""
from src.data.schemas import PlayerProfile


def build_player_rating(player: PlayerProfile) -> dict:
    """
    Convert a PlayerProfile into simulation-ready features.

    For now, this is a simple pass-through with minimal transformation.
    Future versions may include more complex feature engineering.

    Args:
        player: PlayerProfile object

    Returns:
        Dictionary with simulation-ready rating parameters
    """
    # TODO: Add more sophisticated feature engineering in future versions
    # - Historical performance on similar courses
    # - Recent form / momentum
    # - Weather preferences
    # - Course fit metrics
    # - Strokes gained decomposition

    return {
        "player_id": player.player_id,
        "player_name": player.name,
        "skill_rating": player.skill_rating,
        "volatility": player.volatility,
        "birdie_boost": player.birdie_boost,
        "bogey_avoidance": player.bogey_avoidance,
        "par3_skill": player.par3_skill,
        "par4_skill": player.par4_skill,
        "par5_skill": player.par5_skill,
        "consistency": player.consistency,
        "aggression": player.aggression,
    }
