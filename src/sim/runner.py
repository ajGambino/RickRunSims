"""
Monte Carlo runner - runs many tournament simulations and aggregates results.
"""
import random
from typing import List, Optional, Tuple
from collections import defaultdict
from src.data.schemas import TournamentConfig
from src.models.results import SimulationSummaryRow, TournamentSimResult
from src.sim.tournament_engine import simulate_tournament
from src.calibration.diagnostics import TournamentDiagnostics


def run_monte_carlo(
    player_ratings: List[dict],
    config: TournamentConfig,
    num_sims: int,
    seed: Optional[int] = None,
    collect_diagnostics: bool = False,
) -> Tuple[List[SimulationSummaryRow], Optional[TournamentDiagnostics]]:
    """
    Run Monte Carlo simulation of tournament.

    Args:
        player_ratings: List of player rating dicts
        config: TournamentConfig
        num_sims: Number of simulations to run
        seed: Random seed for reproducibility (optional)
        collect_diagnostics: Whether to collect detailed diagnostics (optional)

    Returns:
        Tuple of (summary_rows, diagnostics)
        - summary_rows: List of SimulationSummaryRow objects
        - diagnostics: TournamentDiagnostics object if collect_diagnostics=True, else None
    """
    # Initialize RNG
    base_rng = random.Random(seed)

    # Track stats across all sims
    player_stats = defaultdict(lambda: {
        "wins": 0,
        "top5": 0,
        "top10": 0,
        "made_cut": 0,
        "total_finish": 0,
        "total_score": 0,
        "sims": 0,
        "player_name": "",
    })

    # Initialize diagnostics if requested
    diagnostics = TournamentDiagnostics() if collect_diagnostics else None
    course_par = config.course.total_par

    # Run simulations
    for sim_num in range(num_sims):
        # Create a new RNG for this simulation (for reproducibility)
        sim_seed = base_rng.randint(0, 2**31 - 1)
        sim_rng = random.Random(sim_seed)

        # Run tournament
        result = simulate_tournament(player_ratings, config, sim_rng)

        # Collect diagnostics if requested
        if diagnostics:
            diagnostics.record_tournament(result, course_par)

        # Aggregate stats
        for player_result in result.player_results:
            pid = player_result.player_id
            stats = player_stats[pid]

            # Store player name
            if not stats["player_name"]:
                stats["player_name"] = player_result.player_name

            # Count stats
            stats["sims"] += 1
            stats["total_finish"] += player_result.finish_position
            stats["total_score"] += player_result.total_to_par

            if player_result.finish_position == 1:
                stats["wins"] += 1
            if player_result.finish_position <= 5:
                stats["top5"] += 1
            if player_result.finish_position <= 10:
                stats["top10"] += 1
            if player_result.made_cut:
                stats["made_cut"] += 1

    # Convert to summary rows
    summary_rows = []
    for player_id, stats in player_stats.items():
        n_sims = stats["sims"]

        row = SimulationSummaryRow(
            player_id=player_id,
            player_name=stats["player_name"],
            win_pct=stats["wins"] / n_sims * 100,
            top5_pct=stats["top5"] / n_sims * 100,
            top10_pct=stats["top10"] / n_sims * 100,
            make_cut_pct=stats["made_cut"] / n_sims * 100,
            avg_finish=stats["total_finish"] / n_sims,
            avg_score=stats["total_score"] / n_sims,
            sims=n_sims,
        )
        summary_rows.append(row)

    # Sort by win percentage (descending)
    summary_rows.sort(key=lambda x: x.win_pct, reverse=True)

    return summary_rows, diagnostics
