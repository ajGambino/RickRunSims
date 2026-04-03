"""
One-click demo entrypoint for RickRunSims.

Run this script to execute a full demonstration simulation with:
- Bundled demo data
- 1000 Monte Carlo simulations
- Diagnostics and validation enabled
- Reproducible results (seed=42)
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Run demo simulation using bundled data and standard configuration."""
    print("\n" + "=" * 70)
    print("RickRunSims - Demo Simulation")
    print("=" * 70)
    print("\nStarting demo with bundled data...")
    print("Tournament: Masters 2026")
    print("Simulations: 1,000")
    print("Seed: 42 (reproducible)")
    print("Diagnostics: Enabled")
    print("Validation: Enabled")
    print()

    # Build repo-relative paths
    repo_root = Path(__file__).resolve().parent
    player_csv = repo_root / "data" / "demo" / "players" / "large_field_demo.csv"

    # Construct subprocess command
    cmd = [
        sys.executable,
        "run.py",
        "--tournament", "masters_2026",
        "--sims", "1000",
        "--seed", "42",
        "--player-csv", str(player_csv),
        "--diagnostics",
        "--validate",
    ]

    # Run simulation
    result = subprocess.run(cmd, cwd=repo_root)

    # Print completion message
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("Demo completed successfully!")
        print("=" * 70 + "\n")
    else:
        print("\n" + "=" * 70)
        print(f"Demo failed with exit code {result.returncode}")
        print("=" * 70 + "\n")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
