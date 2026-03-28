"""
Demo data adapter - provides hardcoded sample player field.
This is for demonstration and testing purposes only.
"""
from src.data.schemas import PlayerProfile


def load_demo_field() -> list[PlayerProfile]:
    """
    Return a hardcoded field of demo players with varied skill levels.

    Skill rating scale: 0-100 (higher = better)
    Volatility scale: 0-1 (higher = more variance)
    """
    return [
        # Elite tier
        PlayerProfile("P001", "John Champion", skill_rating=95, volatility=0.3, birdie_boost=0.1, bogey_avoidance=0.15),
        PlayerProfile("P002", "Sarah Eagle", skill_rating=92, volatility=0.25, birdie_boost=0.12, bogey_avoidance=0.1),
        PlayerProfile("P003", "Mike Steady", skill_rating=90, volatility=0.2, birdie_boost=0.05, bogey_avoidance=0.2),

        # Strong tier
        PlayerProfile("P004", "Lisa Birdie", skill_rating=85, volatility=0.35, birdie_boost=0.15, bogey_avoidance=0.05),
        PlayerProfile("P005", "Tom Reliable", skill_rating=83, volatility=0.25, birdie_boost=0.08, bogey_avoidance=0.12),
        PlayerProfile("P006", "Emma Power", skill_rating=82, volatility=0.4, birdie_boost=0.1, bogey_avoidance=0.05),
        PlayerProfile("P007", "David Clutch", skill_rating=80, volatility=0.28, birdie_boost=0.09, bogey_avoidance=0.11),

        # Mid tier
        PlayerProfile("P008", "Rachel Steady", skill_rating=75, volatility=0.3, birdie_boost=0.05, bogey_avoidance=0.08),
        PlayerProfile("P009", "Chris Average", skill_rating=72, volatility=0.35, birdie_boost=0.06, bogey_avoidance=0.06),
        PlayerProfile("P010", "Kelly Consistent", skill_rating=70, volatility=0.25, birdie_boost=0.04, bogey_avoidance=0.09),
        PlayerProfile("P011", "Mark Swinger", skill_rating=68, volatility=0.45, birdie_boost=0.08, bogey_avoidance=0.02),

        # Developing tier
        PlayerProfile("P012", "Anna Rookie", skill_rating=65, volatility=0.4, birdie_boost=0.05, bogey_avoidance=0.05),
        PlayerProfile("P013", "Brian Hopeful", skill_rating=63, volatility=0.38, birdie_boost=0.04, bogey_avoidance=0.06),
        PlayerProfile("P014", "Sophie Grinder", skill_rating=60, volatility=0.32, birdie_boost=0.03, bogey_avoidance=0.07),

        # Long shots
        PlayerProfile("P015", "Jake Underdog", skill_rating=55, volatility=0.5, birdie_boost=0.06, bogey_avoidance=0.03),
        PlayerProfile("P016", "Megan Wildcard", skill_rating=52, volatility=0.55, birdie_boost=0.07, bogey_avoidance=0.02),
    ]
