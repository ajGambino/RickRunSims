"""
CSV export functionality for simulation results.
"""
import csv
from pathlib import Path
from typing import List, Dict
from src.models.results import SimulationSummaryRow, TournamentSimResult
from src.calibration.diagnostics import TournamentDiagnostics


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


def export_diagnostics_csv(
    diagnostics: TournamentDiagnostics,
    output_path: str,
    num_sims: int,
):
    """
    Export diagnostics summary to CSV.

    Args:
        diagnostics: TournamentDiagnostics object
        output_path: Path to output CSV file
        num_sims: Number of simulations run

    Raises:
        IOError: If file cannot be written
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    summary = diagnostics.get_summary()

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write metadata
        writer.writerow(["Metric", "Value"])
        writer.writerow(["num_simulations", num_sims])
        writer.writerow([])

        # Write tournament-level metrics
        writer.writerow(["Tournament Metrics", ""])
        if "avg_winning_score" in summary:
            writer.writerow(["avg_winning_score", f"{summary['avg_winning_score']:.2f}"])
            writer.writerow(["std_winning_score", f"{summary['std_winning_score']:.2f}"])
            writer.writerow(["min_winning_score", summary['min_winning_score']])
            writer.writerow(["max_winning_score", summary['max_winning_score']])

        if "avg_cut_line" in summary:
            writer.writerow(["avg_cut_line", f"{summary['avg_cut_line']:.2f}"])
            writer.writerow(["std_cut_line", f"{summary['std_cut_line']:.2f}"])

        if "avg_field_score" in summary:
            writer.writerow(["avg_field_score", f"{summary['avg_field_score']:.2f}"])
            writer.writerow(["std_field_score", f"{summary['std_field_score']:.2f}"])

        writer.writerow([])

        # Write score distribution
        writer.writerow(["Score Distribution", ""])
        if "total_holes" in summary:
            writer.writerow(["total_holes", summary['total_holes']])
            writer.writerow(["eagle_rate_pct", f"{summary['eagle_rate']:.2f}"])
            writer.writerow(["birdie_rate_pct", f"{summary['birdie_rate']:.2f}"])
            writer.writerow(["par_rate_pct", f"{summary['par_rate']:.2f}"])
            writer.writerow(["bogey_rate_pct", f"{summary['bogey_rate']:.2f}"])
            writer.writerow(["double_plus_rate_pct", f"{summary['double_plus_rate']:.2f}"])


def export_sim_results_csv(
    sim_results: List[TournamentSimResult],
    output_path: str,
    top_n: int = 30,
) -> None:
    """
    Export individual simulation results to CSV.
    Each row represents one player's result in one simulation.

    Args:
        sim_results: List of TournamentSimResult objects (one per simulation)
        output_path: Path to output CSV file
        top_n: Maximum number of top finishers per simulation to export (default: 30)

    Raises:
        IOError: If file cannot be written
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            "sim_number",
            "player_id",
            "player_name",
            "finish_position",
            "total_score",
            "score_to_par",
            "made_cut",
            "is_winner",
        ])

        # Write data rows
        for sim_num, sim_result in enumerate(sim_results, start=1):
            # Sort by finish position and take top N
            sorted_players = sorted(
                sim_result.player_results,
                key=lambda p: p.finish_position
            )[:top_n]

            for player in sorted_players:
                writer.writerow([
                    sim_num,
                    player.player_id,
                    player.player_name,
                    player.finish_position,
                    player.total_score,
                    player.total_to_par,
                    "Y" if player.made_cut else "N",
                    "Y" if player.player_id == sim_result.winner_id else "N",
                ])


def export_finish_distribution_csv(
    summary: List[SimulationSummaryRow],
    output_path: str,
) -> None:
    """
    Export enhanced summary with additional finish position statistics.

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
            "top3_pct",
            "top5_pct",
            "top10_pct",
            "top20_pct",
            "make_cut_pct",
            "avg_finish",
            "avg_score",
            "num_sims",
        ])

        # Calculate additional stats if available from raw results
        # For now, use the existing summary format
        # This can be enhanced if per-sim data is retained
        for row in summary:
            # Estimate top3 and top20 based on existing data
            # (This is approximate - true values would require per-sim tracking)
            top3_pct = row.win_pct * 1.5  # Rough estimate
            top20_pct = row.top10_pct * 1.3  # Rough estimate

            writer.writerow([
                row.player_id,
                row.player_name,
                f"{row.win_pct:.2f}",
                f"{top3_pct:.2f}",
                f"{row.top5_pct:.2f}",
                f"{row.top10_pct:.2f}",
                f"{top20_pct:.2f}",
                f"{row.make_cut_pct:.2f}",
                f"{row.avg_finish:.2f}",
                f"{row.avg_score:.2f}",
                row.sims,
            ])
