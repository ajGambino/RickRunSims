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
from src.outputs.export_csv import export_summary_csv, export_leaderboard_csv, export_diagnostics_csv, export_sim_results_csv, export_finish_distribution_csv
from src.outputs.diagnostics_report import print_diagnostics_summary, print_top_players_diagnostics


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
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Collect and display simulation diagnostics (scoring distributions, winning scores, etc.)",
    )
    parser.add_argument(
        "--export-diagnostics",
        type=str,
        default=None,
        help="Export diagnostics to CSV file (optional)",
    )
    parser.add_argument(
        "--export-sim-results",
        type=str,
        default=None,
        help="Export individual simulation results to CSV file (optional)",
    )
    parser.add_argument(
        "--export-finish-distribution",
        type=str,
        default=None,
        help="Export finish distribution summary with top3/top20 stats to CSV file (optional)",
    )
    parser.add_argument(
        "--sim-results-top",
        type=int,
        default=30,
        help="Number of top finishers per simulation to export (default: 30, only used with --export-sim-results)",
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
        collect_diag = args.diagnostics or args.export_diagnostics is not None
        retain_sims = args.export_sim_results is not None
        summary, diagnostics, sim_results = run_monte_carlo(
            player_ratings=player_ratings,
            config=config,
            num_sims=args.sims,
            seed=args.seed,
            collect_diagnostics=collect_diag,
            retain_sim_results=retain_sims,
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

    # Display diagnostics if requested
    if diagnostics:
        if args.diagnostics:
            print_diagnostics_summary(diagnostics, args.sims)
            print_top_players_diagnostics(diagnostics, player_ratings, top_n=5)

        # Export diagnostics if requested
        if args.export_diagnostics:
            try:
                export_diagnostics_csv(diagnostics, args.export_diagnostics, args.sims)
                exports_written.append(f"Diagnostics: {args.export_diagnostics}")
            except Exception as e:
                print(f"\nError exporting diagnostics: {e}")
                return 1

    # Export sim results if requested
    if args.export_sim_results:
        try:
            export_sim_results_csv(sim_results, args.export_sim_results, top_n=args.sim_results_top)
            exports_written.append(f"Sim Results: {args.export_sim_results}")
        except Exception as e:
            print(f"\n✗ Error exporting sim results: {e}")
            return 1

    # Export finish distribution if requested
    if args.export_finish_distribution:
        try:
            export_finish_distribution_csv(summary, args.export_finish_distribution)
            exports_written.append(f"Finish Distribution: {args.export_finish_distribution}")
        except Exception as e:
            print(f"\n✗ Error exporting finish distribution: {e}")
            return 1

    if exports_written:
        print(f"\nExports written:")
        for export in exports_written:
            print(f"  - {export}")

    return 0


if __name__ == "__main__":
    exit(main())
