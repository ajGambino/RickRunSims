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
import time


def run_monte_carlo(
    player_ratings: List[dict],
    config: TournamentConfig,
    num_sims: int,
    seed: Optional[int] = None,
    collect_diagnostics: bool = False,
    retain_sim_results: bool = False,
) -> Tuple[List[SimulationSummaryRow], Optional[TournamentDiagnostics], Optional[List[TournamentSimResult]]]:

    base_rng = random.Random(seed)

    player_stats: defaultdict = defaultdict(lambda: {
        "wins": 0,
        "top3": 0,
        "top5": 0,
        "top10": 0,
        "top20": 0,
        "made_cut": 0,
        "total_finish": 0,
        "total_score": 0,
        "sims": 0,
        "player_name": "",
    })

    diagnostics = TournamentDiagnostics() if collect_diagnostics else None
    course_par = config.course.total_par

    sim_results = [] if retain_sim_results else None

    # ✅ FIX 1: move start_time OUTSIDE loop
    start_time = time.time()

    # Run simulations
    for sim_num in range(num_sims):

        sim_seed = base_rng.randint(0, 2**31 - 1)
        sim_rng = random.Random(sim_seed)

        result = simulate_tournament(player_ratings, config, sim_rng)

        # ✅ FIX 2: only print every 500 sims
        completed = sim_num + 1
        if completed % 500 == 0 or completed == num_sims:
            elapsed = time.time() - start_time
            sims_per_sec = completed / elapsed if elapsed > 0 else 0
            remaining = (num_sims - completed) / sims_per_sec if sims_per_sec > 0 else 0

            print(
                f"{completed}/{num_sims} sims | "
                f"{sims_per_sec:.2f} sims/sec | "
                f"ETA: {remaining/60:.1f} min"
            )

        if retain_sim_results and sim_results is not None:
            sim_results.append(result)

        if diagnostics:
            diagnostics.record_tournament(result, course_par)

        for player_result in result.player_results:
            pid = player_result.player_id
            stats = player_stats[pid]

            if not stats["player_name"]:
                stats["player_name"] = player_result.player_name

            stats["sims"] = int(stats["sims"]) + 1
            stats["total_finish"] += player_result.finish_position
            stats["total_score"] += player_result.total_to_par

            if player_result.finish_position == 1:
                stats["wins"] += 1
            if player_result.finish_position <= 3:
                stats["top3"] += 1
            if player_result.finish_position <= 5:
                stats["top5"] += 1
            if player_result.finish_position <= 10:
                stats["top10"] += 1
            if player_result.finish_position <= 20:
                stats["top20"] += 1
            if player_result.made_cut:
                stats["made_cut"] += 1

    summary_rows = []
    for player_id, stats in player_stats.items():
        n_sims = stats["sims"]

        row = SimulationSummaryRow(
            player_id=player_id,
            player_name=stats["player_name"],
            win_pct=stats["wins"] / n_sims * 100,
            top3_pct=stats["top3"] / n_sims * 100,
            top5_pct=stats["top5"] / n_sims * 100,
            top10_pct=stats["top10"] / n_sims * 100,
            top20_pct=stats["top20"] / n_sims * 100,
            make_cut_pct=stats["made_cut"] / n_sims * 100,
            avg_finish=stats["total_finish"] / n_sims,
            avg_score=stats["total_score"] / n_sims,
            sims=n_sims,
        )
        summary_rows.append(row)

    summary_rows.sort(key=lambda x: x.win_pct, reverse=True)

    # Debug audit (unchanged)
    from src.sim.hole_engine import simulate_hole
    if hasattr(simulate_hole, 'eagle_prob_count') and simulate_hole.eagle_prob_count > 0:
        avg_eagle_prob = simulate_hole.eagle_prob_sum / simulate_hole.eagle_prob_count
        realized_eagle_rate = simulate_hole.eagle_outcome_count / simulate_hole.total_outcomes
        print(f"\n{'='*80}")
        print(f"EAGLE PROBABILITY AUDIT")
        print(f"{'='*80}")
        print(f"Total holes simulated: {simulate_hole.total_outcomes:,}")
        print(f"Average eagle probability passed to sampling: {avg_eagle_prob:.6f} ({avg_eagle_prob*100:.4f}%)")
        print(f"Realized eagle frequency from sampling: {realized_eagle_rate:.6f} ({realized_eagle_rate*100:.4f}%)")
        print(f"Total eagles sampled: {simulate_hole.eagle_outcome_count:,}")
        print(f"{'='*80}\n")

    return summary_rows, diagnostics, sim_results