"""
RickRunSims - Golf Tournament Monte Carlo Simulator
Main CLI entrypoint.
"""
import argparse
import os
import random
import time
from datetime import datetime

from src.analysis.validation import (
    export_validation_report,
    print_validation_report,
    validate_simulation,
)
from src.data.loader import load_tournament_data
from src.features.rating_builder import build_player_rating
from src.outputs.diagnostics_report import (
    print_diagnostics_summary,
    print_top_players_diagnostics,
)
from src.outputs.export_csv import (
    export_diagnostics_csv,
    export_finish_distribution_csv,
    export_leaderboard_csv,
    export_sim_results_csv,
    export_summary_csv,
)
from src.outputs.reports import print_quick_summary, print_simulation_summary
from src.sim.runner import run_monte_carlo
from src.sim.tournament_engine import simulate_tournament
from src.sim.hole_engine import print_tail_calibration_diagnostics, DEBUG_TAIL_CALIBRATION


def is_private_run(args) -> bool:
    """Return True if this run is using the private raw-data pipeline."""
    return args.raw_player_csv is not None


def configure_private_output_defaults(args) -> str | None:
    """
    For private runs, auto-route exports into a timestamped directory under
    data/private/processed/ unless the user already provided explicit paths.

    Returns:
        The created base directory for this private run, or None if not applicable.
    """
    if not is_private_run(args):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.join("data", "private", "processed", f"run_{timestamp}")
    os.makedirs(base_dir, exist_ok=True)

    # Only set defaults when the user did not explicitly provide a path.
    if not args.export_summary:
        args.export_summary = os.path.join(base_dir, "summary.csv")

    if not args.export_leaderboard:
        args.export_leaderboard = os.path.join(base_dir, "leaderboard.csv")

    if not args.export_diagnostics and (args.diagnostics or args.validate):
        args.export_diagnostics = os.path.join(base_dir, "diagnostics.csv")

    if not args.export_sim_results:
        args.export_sim_results = os.path.join(base_dir, "sim_results.csv")

    if not args.export_finish_distribution:
        args.export_finish_distribution = os.path.join(base_dir, "finish_dist.csv")

    if args.validate and not args.export_validation:
        args.export_validation = os.path.join(base_dir, "validation")

    return base_dir


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
        help="Path to sim-ready CSV file with player data (optional, uses demo data if not specified)",
    )
    parser.add_argument(
        "--raw-player-csv",
        type=str,
        default=None,
        help="Path to raw player statistics CSV (private data pipeline, optional)",
    )
    parser.add_argument(
        "--raw-round-csv",
        type=str,
        default=None,
        help="Path to raw round-by-round CSV for volatility calculation (used with --raw-player-csv, optional)",
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
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation against benchmark targets (requires --diagnostics)",
    )
    parser.add_argument(
        "--validation-config",
        type=str,
        default="masters_baseline",
        help="Validation benchmark configuration to use (default: masters_baseline)",
    )
    parser.add_argument(
        "--export-validation",
        type=str,
        default=None,
        help="Export validation report to directory (optional, requires --validate)",
    )

    args = parser.parse_args()

    # Auto-route outputs for private runs unless explicit export paths were provided.
    private_output_dir = configure_private_output_defaults(args)

    # Print banner
    print("\n" + "=" * 100)
    print("RickRunSims - Golf Tournament Monte Carlo Simulator")
    print("=" * 100)

    if private_output_dir:
        print(f"\nPrivate run detected -> default exports routed to: {private_output_dir}")

    # Load tournament data
    print(f"\nLoading tournament: {args.tournament}...")
    if args.raw_player_csv:
        print(f"Data source: Raw player statistics ({args.raw_player_csv})")
        if args.raw_round_csv:
            print(f"             + Round data ({args.raw_round_csv})")
    elif args.player_csv:
        print(f"Data source: Sim-ready CSV ({args.player_csv})")
    else:
        print("Data source: Built-in demo data")

    try:
        player_field, config = load_tournament_data(
            args.tournament,
            player_csv=args.player_csv,
            raw_player_csv=args.raw_player_csv,
            raw_round_csv=args.raw_round_csv,
        )
        print(f"Loaded {len(player_field)} players")
        print(f"Course: {config.course.name} (Par {config.course.total_par})")
        print(f"Format: {config.num_rounds} rounds")
        if config.cut_after_round:
            print(f"Cut: After round {config.cut_after_round} ({config.cut_rule})")
    except Exception as e:
        print(f"Error loading tournament: {e}")
        return 1

    # Build player ratings
    print("\nPreparing player ratings...")
    player_ratings = [build_player_rating(p) for p in player_field]
    print(f"{len(player_ratings)} players ready")

    # Run simulations
    print(f"\nRunning {args.sims:,} simulations...")
    start_time = time.time()

    try:
        collect_diag = (
            args.diagnostics
            or args.export_diagnostics is not None
            or args.validate
        )
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
        print(f"Error running simulations: {e}")
        import traceback
        traceback.print_exc()
        return 1

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds ({args.sims / elapsed:.0f} sims/sec)")

    # Print tail calibration diagnostics if enabled
    if DEBUG_TAIL_CALIBRATION:
        print_tail_calibration_diagnostics()

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
            print(f"\nError exporting summary: {e}")
            return 1

    if args.export_leaderboard:
        try:
            # Run one representative tournament for leaderboard export
            print("\nGenerating representative tournament leaderboard...")
            rep_seed = args.seed if args.seed is not None else random.randint(0, 2**31 - 1)
            rep_rng = random.Random(rep_seed)
            rep_result = simulate_tournament(player_ratings, config, rep_rng)
            export_leaderboard_csv(rep_result, args.export_leaderboard)
            exports_written.append(f"Leaderboard: {args.export_leaderboard}")
        except Exception as e:
            print(f"\nError exporting leaderboard: {e}")
            return 1

    # Display diagnostics if requested
    if diagnostics:
        if args.diagnostics:
            print_diagnostics_summary(diagnostics, args.sims)
            print_top_players_diagnostics(diagnostics, player_ratings, top_n=5)

        if args.export_diagnostics:
            try:
                export_diagnostics_csv(diagnostics, args.export_diagnostics, args.sims)
                exports_written.append(f"Diagnostics: {args.export_diagnostics}")
            except Exception as e:
                print(f"\nError exporting diagnostics: {e}")
                return 1

        if args.validate:
            try:
                # Load benchmark configuration
                if args.validation_config == "masters_baseline":
                    from src.config.validation.masters_baseline import get_benchmark_config
                    benchmark_config = get_benchmark_config()
                    benchmark_name = "Masters Baseline"
                else:
                    print(f"\nError: Unknown validation config: {args.validation_config}")
                    return 1

                # Run validation
                validation_report = validate_simulation(
                    diagnostics=diagnostics,
                    summary=summary,
                    benchmark_config=benchmark_config,
                    num_sims=args.sims,
                    tournament_name=config.name,
                    benchmark_name=benchmark_name,
                )

                # Print validation report
                print_validation_report(validation_report)

                # Export validation report if requested
                if args.export_validation:
                    export_validation_report(validation_report, args.export_validation)
                    exports_written.append(f"Validation: {args.export_validation}/")

            except Exception as e:
                print(f"\nError running validation: {e}")
                import traceback
                traceback.print_exc()
                return 1

    # Export sim results if requested
    if args.export_sim_results and sim_results is not None:
        try:
            export_sim_results_csv(
                sim_results,
                args.export_sim_results,
                top_n=args.sim_results_top,
            )
            exports_written.append(f"Sim Results: {args.export_sim_results}")
        except Exception as e:
            print(f"\nError exporting sim results: {e}")
            return 1

    # Export finish distribution if requested
    if args.export_finish_distribution:
        try:
            export_finish_distribution_csv(summary, args.export_finish_distribution)
            exports_written.append(
                f"Finish Distribution: {args.export_finish_distribution}"
            )
        except Exception as e:
            print(f"\nError exporting finish distribution: {e}")
            return 1

    if exports_written:
        print("\nExports written:")
        for export in exports_written:
            print(f"  - {export}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())