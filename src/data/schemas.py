"""
Core data schemas for RickRunSims.
Lightweight internal dataclasses for player profiles, courses, and tournament configs.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayerProfile:
    """Profile for a player in the tournament field."""
    player_id: str
    name: str
    skill_rating: float  # Higher = better player (e.g., 0-100 scale)
    volatility: float  # Higher = more variance (e.g., 0-1 scale)
    birdie_boost: float = 0.0  # Optional trait: increases birdie probability
    bogey_avoidance: float = 0.0  # Optional trait: decreases bogey probability


@dataclass
class HoleProfile:
    """Profile for a single hole on a course."""
    hole_number: int
    par: int
    difficulty: float  # Modifier: positive = harder, negative = easier
    yardage: Optional[int] = None  # Optional for now


@dataclass
class CourseProfile:
    """Profile for a golf course."""
    course_id: str
    name: str
    holes: list[HoleProfile]

    @property
    def total_par(self) -> int:
        return sum(hole.par for hole in self.holes)


@dataclass
class TournamentConfig:
    """Configuration for a tournament."""
    tournament_id: str
    name: str
    course: CourseProfile
    num_rounds: int
    cut_after_round: Optional[int] = None  # None = no cut
    cut_rule: Optional[str] = None  # e.g., "top_50_and_ties"
