"""
RickRunSims - Golf Tournament Monte Carlo Simulator
Main CLI entrypoint.
"""
import argparse
import time
import random
from src.data.loader import load_tournament_data
from src.features.rating_builder import build_player_rating
from src.sim.runner import run_monte_carlo
from src.sim.tournament_engine import simulate_tournament
from src.outputs.reports import print_simulation_summary, print_quick_summary
from src.outputs.export_csv import export_summary_csv, export_leaderboard_csv


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Run Monte Carlo golf tournament simulation"
    )
    parser.add_argument(
        "--tournament",
        type=str,
        default="masters_2026",
        help="Tournament to simulate (default: masters_2026)",
    )
    parser.add_argument(
        "--sims",
        type=int,
        default=1000,
        help="Number of simulations to run (default: 1000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of top players to display (default: 20)",
    )
    parser.add_argument(
        "--player-csv",
        type=str,
        default=None,
        help="Path to CSV file with player data (optional, uses demo data if not specified)",
    )
    parser.add_argument(
        "--export-summary",
        type=str,
        default=None,
        help="Export Monte Carlo summary to CSV file (optional)",
    )
    parser.add_argument(
        "--export-leaderboard",
        type=str,
        default=None,
        help="Export a representative tournament leaderboard to CSV file (optional)",
    )

    args = parser.parse_args()

    # Print banner
    print("\n" + "=" * 100)
    print("RickRunSims - Golf Tournament Monte Carlo Simulator")
    print("=" * 100)

    # Load tournament data
    print(f"\nLoading tournament: {args.tournament}...")
    if args.player_csv:
        print(f"Data source: Custom CSV ({args.player_csv})")
    else:
        print("Data source: Built-in demo data")

    try:
        player_field, config = load_tournament_data(args.tournament, player_csv=args.player_csv)
        print(f" Loaded {len(player_field)} players")
        print(f" Course: {config.course.name} (Par {config.course.total_par})")
        print(f" Format: {config.num_rounds} rounds")
        if config.cut_after_round:
            print(f" Cut: After round {config.cut_after_round} ({config.cut_rule})")
    except Exception as e:
        print(f" Error loading tournament: {e}")
        return 1

    # Build player ratings
    print("\nPreparing player ratings...")
    player_ratings = [build_player_rating(p) for p in player_field]
    print(f" {len(player_ratings)} players ready")

    # Run simulations
    print(f"\nRunning {args.sims:,} simulations...")
    start_time = time.time()

    try:
        summary = run_monte_carlo(
            player_ratings=player_ratings,
            config=config,
            num_sims=args.sims,
            seed=args.seed,
        )
    except Exception as e:
        print(f" Error running simulations: {e}")
        import traceback
        traceback.print_exc()
        return 1

    elapsed = time.time() - start_time
    print(f" Completed in {elapsed:.2f} seconds ({args.sims / elapsed:.0f} sims/sec)")

    # Display results
    print_simulation_summary(summary, config.name, args.sims, top_n=args.top)
    print_quick_summary(summary, top_n=5)

    # Export results if requested
    exports_written = []

    if args.export_summary:
        try:
            export_summary_csv(summary, args.export_summary)
            exports_written.append(f"Summary: {args.export_summary}")
        except Exception as e:
            print(f"\n✗ Error exporting summary: {e}")
            return 1

    if args.export_leaderboard:
        try:
            # Run one representative tournament for leaderboard export
            print(f"\nGenerating representative tournament leaderboard...")
            rep_seed = args.seed if args.seed else random.randint(0, 2**31 - 1)
            rep_rng = random.Random(rep_seed)
            rep_result = simulate_tournament(player_ratings, config, rep_rng)
            export_leaderboard_csv(rep_result, args.export_leaderboard)
            exports_written.append(f"Leaderboard: {args.export_leaderboard}")
        except Exception as e:
            print(f"\n✗ Error exporting leaderboard: {e}")
            return 1

    if exports_written:
        print(f"\nExports written:")
        for export in exports_written:
            print(f"  - {export}")

    return 0


if __name__ == "__main__":
    exit(main())
