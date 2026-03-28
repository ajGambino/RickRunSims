"""
RickRunSims - Golf Tournament Monte Carlo Simulator
Main CLI entrypoint.
"""
import argparse
import time
from src.data.loader import load_tournament_data
from src.features.rating_builder import build_player_rating
from src.sim.runner import run_monte_carlo
from src.outputs.reports import print_simulation_summary, print_quick_summary


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

    args = parser.parse_args()

    # Print banner
    print("\n" + "=" * 100)
    print("RickRunSims - Golf Tournament Monte Carlo Simulator")
    print("=" * 100)

    # Load tournament data
    print(f"\nLoading tournament: {args.tournament}...")
    try:
        player_field, config = load_tournament_data(args.tournament)
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

    return 0


if __name__ == "__main__":
    exit(main())
