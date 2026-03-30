"""
Result models for tournament simulation.
Runtime objects tracking player performance and aggregated statistics.
"""
from dataclasses import dataclass, field


@dataclass
class PlayerRoundResult:
    """Result for one player's round."""
    player_id: str
    player_name: str
    round_number: int
    hole_scores: list[int]  # Absolute score for each hole
    hole_outcomes: list[str] = field(default_factory=list)  # Categorical outcome for each hole (eagle/birdie/par/bogey/double)

    @property
    def total_score(self) -> int:
        return sum(self.hole_scores)

    @property
    def score_to_par(self) -> int:
        """Score relative to par (calculated by tournament engine)."""
        # Will be set by tournament engine which knows the course par
        return getattr(self, '_score_to_par', 0)


@dataclass
class PlayerTournamentResult:
    """Result for one player's complete tournament."""
    player_id: str
    player_name: str
    rounds: list[PlayerRoundResult]
    made_cut: bool
    finish_position: int = 0  # 1 = winner, 0 = not yet determined

    @property
    def total_score(self) -> int:
        return sum(r.total_score for r in self.rounds)

    @property
    def total_to_par(self) -> int:
        """Total score relative to par."""
        return sum(getattr(r, '_score_to_par', 0) for r in self.rounds)


@dataclass
class SimulationSummaryRow:
    """Aggregated statistics for one player across many simulations."""
    player_id: str
    player_name: str
    win_pct: float = 0.0
    top3_pct: float = 0.0
    top5_pct: float = 0.0
    top10_pct: float = 0.0
    top20_pct: float = 0.0
    make_cut_pct: float = 0.0
    avg_finish: float = 0.0
    avg_score: float = 0.0
    sims: int = 0


@dataclass
class TournamentSimResult:
    """Result of a single tournament simulation."""
    tournament_id: str
    player_results: list[PlayerTournamentResult]
    winner_id: str = ""
    winner_name: str = ""
    winning_score: int = 0
