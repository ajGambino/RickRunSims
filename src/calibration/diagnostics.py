"""
Simulation diagnostics - measures realism of tournament outcomes.

This module tracks and reports statistics to evaluate whether the simulation
produces realistic score distributions, winning scores, cut lines, etc.

This is NOT about fitting or ML - just basic measurement.
"""
from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict
import statistics


@dataclass
class TournamentDiagnostics:
    """Aggregate diagnostics across all simulations."""

    # Tournament-level metrics
    winning_scores: List[int] = field(default_factory=list)
    cut_lines: List[int] = field(default_factory=list)
    field_avg_scores: List[float] = field(default_factory=list)

    # Score distribution (global across all players/holes)
    total_holes: int = 0
    eagles: int = 0
    birdies: int = 0
    pars: int = 0
    bogeys: int = 0
    doubles_plus: int = 0

    # Player-level tracking
    player_round_scores: Dict[str, List[int]] = field(default_factory=lambda: defaultdict(list))
    player_hole_outcomes: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {
        "eagles": 0,
        "birdies": 0,
        "pars": 0,
        "bogeys": 0,
        "doubles_plus": 0,
        "total_holes": 0,
    }))

    def record_tournament(self, tournament_result, course_par: int):
        """
        Record diagnostics from a single tournament simulation.

        Args:
            tournament_result: TournamentSimResult object
            course_par: Par for the course
        """
        # Record winning score
        if tournament_result.player_results:
            self.winning_scores.append(tournament_result.winning_score)

        # Calculate field average
        completed_players = [p for p in tournament_result.player_results if len(p.rounds) > 0]
        if completed_players:
            field_avg = sum(p.total_to_par for p in completed_players) / len(completed_players)
            self.field_avg_scores.append(field_avg)

        # Record cut line (score of last player who made cut)
        cut_players = [p for p in tournament_result.player_results if p.made_cut]
        if cut_players:
            cut_line_score = max(p.total_to_par for p in cut_players if len(p.rounds) >= 2)
            self.cut_lines.append(cut_line_score)

        # Process each player's rounds for detailed stats
        for player_result in tournament_result.player_results:
            player_id = player_result.player_id

            for round_result in player_result.rounds:
                # Record round score to par
                round_to_par = getattr(round_result, '_score_to_par', 0)
                self.player_round_scores[player_id].append(round_to_par)

                # Analyze hole-by-hole outcomes
                for hole_score in round_result.hole_scores:
                    hole_idx = len([s for s in round_result.hole_scores if round_result.hole_scores.index(hole_score) >= round_result.hole_scores.index(s)])
                    # Infer hole par from score and course structure
                    # For simplicity, we'll compute score relative to par from the aggregate
                    # Since we don't have direct hole par here, we'll track raw outcomes
                    pass

                # Track score distributions from categorical outcomes
                # Use the actual sampled outcome categories from simulation
                for outcome in round_result.hole_outcomes:
                    self.total_holes += 1

                    # Classify based on actual simulation outcome, not inferred from absolute score
                    if outcome == "eagle":
                        self.eagles += 1
                        self.player_hole_outcomes[player_id]["eagles"] += 1
                    elif outcome == "birdie":
                        self.birdies += 1
                        self.player_hole_outcomes[player_id]["birdies"] += 1
                    elif outcome == "par":
                        self.pars += 1
                        self.player_hole_outcomes[player_id]["pars"] += 1
                    elif outcome == "bogey":
                        self.bogeys += 1
                        self.player_hole_outcomes[player_id]["bogeys"] += 1
                    elif outcome == "double":
                        self.doubles_plus += 1
                        self.player_hole_outcomes[player_id]["doubles_plus"] += 1

                    self.player_hole_outcomes[player_id]["total_holes"] += 1

    def get_summary(self) -> Dict:
        """
        Compute summary statistics from collected diagnostics.

        Returns:
            Dictionary with diagnostic metrics
        """
        summary = {}

        # Tournament-level metrics
        if self.winning_scores:
            summary["avg_winning_score"] = statistics.mean(self.winning_scores)
            summary["std_winning_score"] = statistics.stdev(self.winning_scores) if len(self.winning_scores) > 1 else 0.0
            summary["min_winning_score"] = min(self.winning_scores)
            summary["max_winning_score"] = max(self.winning_scores)

        if self.cut_lines:
            summary["avg_cut_line"] = statistics.mean(self.cut_lines)
            summary["std_cut_line"] = statistics.stdev(self.cut_lines) if len(self.cut_lines) > 1 else 0.0

        if self.field_avg_scores:
            summary["avg_field_score"] = statistics.mean(self.field_avg_scores)
            summary["std_field_score"] = statistics.stdev(self.field_avg_scores) if len(self.field_avg_scores) > 1 else 0.0

        # Global score distribution
        if self.total_holes > 0:
            summary["eagle_rate"] = (self.eagles / self.total_holes) * 100
            summary["birdie_rate"] = (self.birdies / self.total_holes) * 100
            summary["par_rate"] = (self.pars / self.total_holes) * 100
            summary["bogey_rate"] = (self.bogeys / self.total_holes) * 100
            summary["double_plus_rate"] = (self.doubles_plus / self.total_holes) * 100
            summary["total_holes"] = self.total_holes

        return summary

    def get_player_summary(self, player_id: str, player_name: str) -> Dict:
        """
        Get diagnostics for a specific player.

        Args:
            player_id: Player identifier
            player_name: Player name

        Returns:
            Dictionary with player-specific metrics
        """
        summary = {"player_id": player_id, "player_name": player_name}

        # Round score statistics
        if player_id in self.player_round_scores and self.player_round_scores[player_id]:
            scores = self.player_round_scores[player_id]
            summary["avg_round_score"] = statistics.mean(scores)
            summary["std_round_score"] = statistics.stdev(scores) if len(scores) > 1 else 0.0
            summary["rounds_played"] = len(scores)

        # Hole outcome rates
        if player_id in self.player_hole_outcomes:
            outcomes = self.player_hole_outcomes[player_id]
            total = outcomes["total_holes"]
            if total > 0:
                summary["eagle_rate"] = (outcomes["eagles"] / total) * 100
                summary["birdie_rate"] = (outcomes["birdies"] / total) * 100
                summary["par_rate"] = (outcomes["pars"] / total) * 100
                summary["bogey_rate"] = (outcomes["bogeys"] / total) * 100
                summary["double_plus_rate"] = (outcomes["doubles_plus"] / total) * 100
                summary["total_holes"] = total

        return summary
