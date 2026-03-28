"""
Console output reports - pretty-print simulation results.
"""
from typing import List
from src.models.results import SimulationSummaryRow


def print_simulation_summary(
    summary: List[SimulationSummaryRow],
    tournament_name: str,
    num_sims: int,
    top_n: int = 20,
):
    """
    Print a formatted summary table to console.

    Args:
        summary: List of SimulationSummaryRow objects (sorted by win %)
        tournament_name: Name of tournament
        num_sims: Number of simulations run
        top_n: Number of top players to display
    """
    print("\n" + "=" * 100)
    print(f"{tournament_name} - Monte Carlo Simulation Results")
    print(f"Simulations: {num_sims:,}")
    print("=" * 100)
    print()

    # Header
    header = (
        f"{'Rank':<6} {'Player':<25} {'Win %':>8} {'Top 5%':>8} {'Top 10%':>9} "
        f"{'Make Cut%':>10} {'Avg Finish':>11} {'Avg Score':>10}"
    )
    print(header)
    print("-" * 100)

    # Rows
    for i, row in enumerate(summary[:top_n], 1):
        line = (
            f"{i:<6} {row.player_name:<25} {row.win_pct:>7.2f}% {row.top5_pct:>7.2f}% "
            f"{row.top10_pct:>8.2f}% {row.make_cut_pct:>9.2f}% {row.avg_finish:>11.1f} "
            f"{row.avg_score:>+10.2f}"
        )
        print(line)

    print("-" * 100)
    print()


def print_quick_summary(summary: List[SimulationSummaryRow], top_n: int = 5):
    """
    Print a quick summary of top contenders and field statistics.

    Args:
        summary: List of SimulationSummaryRow objects
        top_n: Number of favorites to show
    """
    print(f"\nTop {top_n} Favorites:")
    for i, row in enumerate(summary[:top_n], 1):
        print(f"  {i}. {row.player_name}: {row.win_pct:.1f}% win probability")

    # Field statistics
    if summary:
        avg_cut_pct = sum(r.make_cut_pct for r in summary) / len(summary)
        avg_score = sum(r.avg_score for r in summary) / len(summary)
        print(f"\nField Statistics:")
        print(f"  Average make cut %: {avg_cut_pct:.1f}%")
        print(f"  Average score to par: {avg_score:+.2f}")
    print()
