"""
Analysis utilities for inspecting simulation results.

This module provides lightweight tools for analyzing simulation outputs,
including distribution analysis, scoring statistics, and outcome summaries.
"""
import csv
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict, Counter


def load_summary_csv(file_path: str) -> List[Dict]:
    """
    Load simulation summary CSV into list of dicts.

    Args:
        file_path: Path to summary CSV file

    Returns:
        List of player summary dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def analyze_winning_scores(file_path: str, top_n: int = 10) -> None:
    """
    Analyze winning score distributions from simulation results.

    Args:
        file_path: Path to CSV file (summary or sim results)
        top_n: Number of top winners to show
    """
    data = load_summary_csv(file_path)

    # Sort by win percentage
    sorted_data = sorted(
        data,
        key=lambda x: float(x.get('win_pct', 0)),
        reverse=True
    )[:top_n]

    print("\nTop Winning Probabilities:")
    print("-" * 80)
    print(f"{'Player':<25} {'Win %':>10} {'Top 5%':>10} {'Top 10%':>10} {'Avg Score':>12}")
    print("-" * 80)

    for row in sorted_data:
        name = row['player_name'][:24]
        win_pct = float(row['win_pct'])
        top5_pct = float(row['top5_pct'])
        top10_pct = float(row['top10_pct'])
        avg_score = float(row['avg_score'])

        print(f"{name:<25} {win_pct:>9.2f}% {top5_pct:>9.2f}% {top10_pct:>9.2f}% {avg_score:>+11.2f}")


def analyze_cut_likelihood(file_path: str, threshold: float = 50.0) -> None:
    """
    Analyze players' cut-making probabilities.

    Args:
        file_path: Path to summary CSV file
        threshold: Minimum cut % to display (default: 50.0)
    """
    data = load_summary_csv(file_path)

    # Filter and sort by make cut percentage
    filtered = [
        row for row in data
        if float(row.get('make_cut_pct', 0)) >= threshold
    ]
    sorted_data = sorted(
        filtered,
        key=lambda x: float(x['make_cut_pct']),
        reverse=True
    )

    print(f"\nPlayers with >={threshold}% Cut Probability:")
    print("-" * 80)
    print(f"{'Player':<25} {'Make Cut %':>12} {'Avg Finish':>12} {'Avg Score':>12}")
    print("-" * 80)

    for row in sorted_data:
        name = row['player_name'][:24]
        cut_pct = float(row['make_cut_pct'])
        avg_finish = float(row['avg_finish'])
        avg_score = float(row['avg_score'])

        print(f"{name:<25} {cut_pct:>11.2f}% {avg_finish:>12.1f} {avg_score:>+11.2f}")


def analyze_score_distribution(file_path: str) -> None:
    """
    Analyze overall score distribution from summary CSV.

    Args:
        file_path: Path to summary CSV file
    """
    data = load_summary_csv(file_path)

    scores = [float(row['avg_score']) for row in data if 'avg_score' in row]

    if not scores:
        print("No score data found")
        return

    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)

    print("\nField Score Distribution:")
    print("-" * 80)
    print(f"  Number of players: {len(scores)}")
    print(f"  Average score (to par): {avg_score:+.2f}")
    print(f"  Best avg score: {min_score:+.2f}")
    print(f"  Worst avg score: {max_score:+.2f}")
    print(f"  Range: {max_score - min_score:.2f} strokes")


def analyze_finish_distribution(file_path: str, positions: List[int] = None) -> None:
    """
    Analyze finish position distributions.

    Args:
        file_path: Path to summary CSV file
        positions: List of positions to highlight (default: [1, 5, 10, 20])
    """
    if positions is None:
        positions = [1, 5, 10, 20]

    data = load_summary_csv(file_path)

    print("\nFinish Position Distribution:")
    print("-" * 80)

    for pos in positions:
        # Count players with avg finish <= position
        count = sum(1 for row in data if float(row.get('avg_finish', 999)) <= pos)
        pct = (count / len(data) * 100) if data else 0

        print(f"  Players averaging top {pos:>2}: {count:>3} ({pct:>5.1f}%)")


def compare_players(file_path: str, player_ids: List[str]) -> None:
    """
    Compare specific players side-by-side.

    Args:
        file_path: Path to summary CSV file
        player_ids: List of player IDs to compare
    """
    data = load_summary_csv(file_path)

    # Filter to requested players
    players = [row for row in data if row['player_id'] in player_ids]

    if not players:
        print(f"No players found with IDs: {player_ids}")
        return

    print("\nPlayer Comparison:")
    print("-" * 100)
    print(f"{'Player':<20} {'Win %':>10} {'Top 5%':>10} {'Top 10%':>10} {'Cut %':>10} {'Avg Finish':>12} {'Avg Score':>12}")
    print("-" * 100)

    for row in players:
        name = row['player_name'][:19]
        win_pct = float(row['win_pct'])
        top5_pct = float(row['top5_pct'])
        top10_pct = float(row['top10_pct'])
        cut_pct = float(row['make_cut_pct'])
        avg_finish = float(row['avg_finish'])
        avg_score = float(row['avg_score'])

        print(f"{name:<20} {win_pct:>9.2f}% {top5_pct:>9.2f}% {top10_pct:>9.2f}% {cut_pct:>9.2f}% {avg_finish:>12.1f} {avg_score:>+11.2f}")


def quick_summary(file_path: str) -> None:
    """
    Print a quick summary of simulation results.

    Args:
        file_path: Path to summary CSV file
    """
    data = load_summary_csv(file_path)

    if not data:
        print("No data found")
        return

    num_sims = int(data[0].get('num_sims', 0))
    num_players = len(data)

    # Get top winner
    top_winner = max(data, key=lambda x: float(x['win_pct']))

    # Calculate field stats
    avg_field_score = sum(float(row['avg_score']) for row in data) / num_players

    print("\n" + "=" * 80)
    print("Simulation Summary")
    print("=" * 80)
    print(f"  Simulations run: {num_sims:,}")
    print(f"  Players in field: {num_players}")
    print(f"  Field avg score: {avg_field_score:+.2f}")
    print(f"\n  Favorite to win: {top_winner['player_name']}")
    print(f"    Win probability: {float(top_winner['win_pct']):.2f}%")
    print(f"    Top 10 probability: {float(top_winner['top10_pct']):.2f}%")
    print("=" * 80)


def main():
    """
    CLI entrypoint for analysis utilities.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze RickRunSims simulation results"
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to summary CSV file",
    )
    parser.add_argument(
        "--command",
        type=str,
        choices=['summary', 'winners', 'cuts', 'scores', 'finishes', 'compare'],
        default='summary',
        help="Analysis command to run",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top results to show (for winners)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=50.0,
        help="Threshold percentage for cut analysis",
    )
    parser.add_argument(
        "--players",
        type=str,
        nargs='+',
        help="Player IDs for comparison",
    )

    args = parser.parse_args()

    # Check file exists
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        return 1

    # Run requested analysis
    if args.command == 'summary':
        quick_summary(args.file)
    elif args.command == 'winners':
        analyze_winning_scores(args.file, top_n=args.top)
    elif args.command == 'cuts':
        analyze_cut_likelihood(args.file, threshold=args.threshold)
    elif args.command == 'scores':
        analyze_score_distribution(args.file)
    elif args.command == 'finishes':
        analyze_finish_distribution(args.file)
    elif args.command == 'compare':
        if not args.players:
            print("Error: --players required for compare command")
            return 1
        compare_players(args.file, args.players)

    return 0


if __name__ == "__main__":
    exit(main())
