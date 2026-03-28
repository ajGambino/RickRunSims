"""
Console output for diagnostics - prints simulation calibration metrics.
"""
from typing import Optional
from src.calibration.diagnostics import TournamentDiagnostics


def print_diagnostics_summary(diagnostics: TournamentDiagnostics, num_sims: int):
    """
    Print diagnostics summary to console.

    Args:
        diagnostics: TournamentDiagnostics object with collected metrics
        num_sims: Number of simulations run
    """
    summary = diagnostics.get_summary()

    if not summary:
        print("\nNo diagnostics data available")
        return

    print("\n" + "=" * 100)
    print(f"Simulation Diagnostics ({num_sims:,} simulations)")
    print("=" * 100)

    # Tournament-level metrics
    print("\nTournament Metrics:")
    print("-" * 100)

    if "avg_winning_score" in summary:
        print(f"  Winning Score (to par):")
        print(f"    Average:         {summary['avg_winning_score']:+.2f}")
        print(f"    Std Dev:         {summary['std_winning_score']:.2f}")
        print(f"    Range:           {summary['min_winning_score']:+d} to {summary['max_winning_score']:+d}")

    if "avg_cut_line" in summary:
        print(f"\n  Cut Line (to par):")
        print(f"    Average:         {summary['avg_cut_line']:+.2f}")
        print(f"    Std Dev:         {summary['std_cut_line']:.2f}")

    if "avg_field_score" in summary:
        print(f"\n  Field Average (to par):")
        print(f"    Average:         {summary['avg_field_score']:+.2f}")
        print(f"    Std Dev:         {summary['std_field_score']:.2f}")

    # Score distribution
    print("\n\nScore Distribution (All Players, All Holes):")
    print("-" * 100)

    if "total_holes" in summary:
        print(f"  Total Holes:     {summary['total_holes']:,}")
        print(f"  Eagle Rate:      {summary['eagle_rate']:.2f}%")
        print(f"  Birdie Rate:     {summary['birdie_rate']:.2f}%")
        print(f"  Par Rate:        {summary['par_rate']:.2f}%")
        print(f"  Bogey Rate:      {summary['bogey_rate']:.2f}%")
        print(f"  Double+ Rate:    {summary['double_plus_rate']:.2f}%")

    print("\n" + "=" * 100)


def print_player_diagnostics(
    diagnostics: TournamentDiagnostics,
    player_id: str,
    player_name: str
):
    """
    Print diagnostics for a specific player.

    Args:
        diagnostics: TournamentDiagnostics object
        player_id: Player identifier
        player_name: Player name
    """
    player_summary = diagnostics.get_player_summary(player_id, player_name)

    if not player_summary or len(player_summary) <= 2:  # Only has id and name
        print(f"\nNo diagnostics data for {player_name}")
        return

    print(f"\nPlayer Diagnostics: {player_name}")
    print("-" * 60)

    if "avg_round_score" in player_summary:
        print(f"  Avg Round Score (to par): {player_summary['avg_round_score']:+.2f}")
        print(f"  Std Dev:                  {player_summary['std_round_score']:.2f}")
        print(f"  Rounds Played:            {player_summary['rounds_played']}")

    if "total_holes" in player_summary:
        print(f"\n  Score Distribution ({player_summary['total_holes']} holes):")
        print(f"    Eagle Rate:    {player_summary['eagle_rate']:.2f}%")
        print(f"    Birdie Rate:   {player_summary['birdie_rate']:.2f}%")
        print(f"    Par Rate:      {player_summary['par_rate']:.2f}%")
        print(f"    Bogey Rate:    {player_summary['bogey_rate']:.2f}%")
        print(f"    Double+ Rate:  {player_summary['double_plus_rate']:.2f}%")


def print_top_players_diagnostics(
    diagnostics: TournamentDiagnostics,
    player_ratings: list,
    top_n: int = 5
):
    """
    Print diagnostics for top N players by skill rating.

    Args:
        diagnostics: TournamentDiagnostics object
        player_ratings: List of player rating dicts
        top_n: Number of top players to show
    """
    # Sort by skill rating
    sorted_players = sorted(
        player_ratings,
        key=lambda p: p["skill_rating"],
        reverse=True
    )[:top_n]

    print(f"\nTop {top_n} Players Diagnostics (by skill rating):")
    print("=" * 100)

    for player in sorted_players:
        print_player_diagnostics(
            diagnostics,
            player["player_id"],
            player["player_name"]
        )
