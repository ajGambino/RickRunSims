"""
CSV export functionality for simulation results.
"""
import csv
from pathlib import Path
from typing import List
from src.models.results import SimulationSummaryRow, TournamentSimResult


def export_summary_csv(
    summary: List[SimulationSummaryRow],
    output_path: str,
) -> None:
    """
    Export Monte Carlo simulation summary to CSV.

    Args:
        summary: List of SimulationSummaryRow objects
        output_path: Path to output CSV file

    Raises:
        IOError: If file cannot be written
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            "player_id",
            "player_name",
            "win_pct",
            "top5_pct",
            "top10_pct",
            "make_cut_pct",
            "avg_finish",
            "avg_score",
            "num_sims",
        ])

        # Write data rows
        for row in summary:
            writer.writerow([
                row.player_id,
                row.player_name,
                f"{row.win_pct:.2f}",
                f"{row.top5_pct:.2f}",
                f"{row.top10_pct:.2f}",
                f"{row.make_cut_pct:.2f}",
                f"{row.avg_finish:.2f}",
                f"{row.avg_score:.2f}",
                row.sims,
            ])


def export_leaderboard_csv(
    tournament_result: TournamentSimResult,
    output_path: str,
) -> None:
    """
    Export a single tournament leaderboard to CSV.

    Args:
        tournament_result: TournamentSimResult object
        output_path: Path to output CSV file

    Raises:
        IOError: If file cannot be written
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            "position",
            "player_id",
            "player_name",
            "total_score",
            "score_to_par",
            "made_cut",
            "round1",
            "round2",
            "round3",
            "round4",
        ])

        # Write data rows (sorted by finish position)
        sorted_players = sorted(
            tournament_result.player_results,
            key=lambda p: p.finish_position
        )

        for player in sorted_players:
            # Get round scores (to par)
            round_scores = [
                getattr(r, '_score_to_par', 0) for r in player.rounds
            ]
            # Pad with empty strings if player missed cut
            while len(round_scores) < 4:
                round_scores.append("")

            writer.writerow([
                player.finish_position,
                player.player_id,
                player.player_name,
                player.total_score,
                player.total_to_par,
                "Y" if player.made_cut else "N",
                round_scores[0] if len(round_scores) > 0 else "",
                round_scores[1] if len(round_scores) > 1 else "",
                round_scores[2] if len(round_scores) > 2 else "",
                round_scores[3] if len(round_scores) > 3 else "",
            ])
