"""
Validation harness - compares simulation outputs against benchmark targets.

This module provides tools to validate that simulation outputs match expected
tournament behavior and identify areas where calibration is needed.
"""
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from src.calibration.diagnostics import TournamentDiagnostics
from src.models.results import SimulationSummaryRow


@dataclass
class ValidationCheck:
    """Result of a single validation check."""
    metric_name: str
    simulated_value: float
    target_value: Optional[float] = None
    target_range: Optional[Tuple[float, float]] = None
    units: str = ""
    description: str = ""
    passed: bool = False
    error: float = 0.0
    error_pct: Optional[float] = None

    @property
    def status(self) -> str:
        """Human-readable status."""
        return "PASS" if self.passed else "FAIL"

    @property
    def error_direction(self) -> str:
        """Direction of error (too high/too low)."""
        if self.error == 0:
            return "exact"
        elif self.error > 0:
            return "too high"
        else:
            return "too low"


@dataclass
class ValidationReport:
    """Complete validation report with all checks and summary."""
    checks: List[ValidationCheck] = field(default_factory=list)
    num_simulations: int = 0
    tournament_name: str = ""
    benchmark_name: str = ""

    @property
    def num_passed(self) -> int:
        """Number of checks that passed."""
        return sum(1 for check in self.checks if check.passed)

    @property
    def num_failed(self) -> int:
        """Number of checks that failed."""
        return sum(1 for check in self.checks if not check.passed)

    @property
    def pass_rate(self) -> float:
        """Percentage of checks passed."""
        if not self.checks:
            return 0.0
        return (self.num_passed / len(self.checks)) * 100

    def get_worst_misses(self, n: int = 5) -> List[ValidationCheck]:
        """Get the N worst misses by absolute error percentage."""
        failed = [c for c in self.checks if not c.passed and c.error_pct is not None]
        return sorted(failed, key=lambda c: abs(c.error_pct), reverse=True)[:n]


def validate_simulation(
    diagnostics: TournamentDiagnostics,
    summary: List[SimulationSummaryRow],
    benchmark_config: Dict,
    num_sims: int,
    tournament_name: str = "Unknown",
    benchmark_name: str = "Unknown"
) -> ValidationReport:
    """
    Validate simulation results against benchmark targets.

    Args:
        diagnostics: TournamentDiagnostics with collected metrics
        summary: List of SimulationSummaryRow objects
        benchmark_config: Benchmark configuration dictionary
        num_sims: Number of simulations run
        tournament_name: Tournament identifier
        benchmark_name: Benchmark identifier

    Returns:
        ValidationReport with all checks and results
    """
    report = ValidationReport(
        num_simulations=num_sims,
        tournament_name=tournament_name,
        benchmark_name=benchmark_name
    )

    # Get diagnostic summary
    diag_summary = diagnostics.get_summary()

    # Validate tournament-level metrics
    if "avg_winning_score" in diag_summary and "winning_score" in benchmark_config:
        report.checks.append(_check_metric(
            "winning_score",
            diag_summary["avg_winning_score"],
            benchmark_config["winning_score"]
        ))

    if "avg_cut_line" in diag_summary and "cut_line" in benchmark_config:
        report.checks.append(_check_metric(
            "cut_line",
            diag_summary["avg_cut_line"],
            benchmark_config["cut_line"]
        ))

    if "avg_field_score" in diag_summary and "field_avg" in benchmark_config:
        report.checks.append(_check_metric(
            "field_avg",
            diag_summary["avg_field_score"],
            benchmark_config["field_avg"]
        ))

    # Validate score distribution metrics
    score_dist_metrics = [
        ("eagle_rate", "eagle_rate"),
        ("birdie_rate", "birdie_rate"),
        ("par_rate", "par_rate"),
        ("bogey_rate", "bogey_rate"),
        ("double_plus_rate", "double_plus_rate")
    ]

    for diag_key, bench_key in score_dist_metrics:
        if diag_key in diag_summary and bench_key in benchmark_config:
            report.checks.append(_check_metric(
                bench_key,
                diag_summary[diag_key],
                benchmark_config[bench_key]
            ))

    # Validate competition structure (if benchmarks exist)
    if "top_player_win_pct_max" in benchmark_config:
        max_win_pct = max(row.win_pct for row in summary) if summary else 0
        check = ValidationCheck(
            metric_name="top_player_win_pct_max",
            simulated_value=max_win_pct,
            target_value=benchmark_config["top_player_win_pct_max"]["target"],
            units=benchmark_config["top_player_win_pct_max"]["units"],
            description=benchmark_config["top_player_win_pct_max"]["description"],
            passed=max_win_pct <= benchmark_config["top_player_win_pct_max"]["target"],
            error=max_win_pct - benchmark_config["top_player_win_pct_max"]["target"]
        )
        if check.target_value and check.target_value != 0:
            check.error_pct = (check.error / check.target_value) * 100
        report.checks.append(check)

    if "field_win_concentration_min" in benchmark_config:
        win_concentration = sum(1 for row in summary if row.win_pct > 2.0)
        check = ValidationCheck(
            metric_name="field_win_concentration_min",
            simulated_value=win_concentration,
            target_value=benchmark_config["field_win_concentration_min"]["target"],
            units=benchmark_config["field_win_concentration_min"]["units"],
            description=benchmark_config["field_win_concentration_min"]["description"],
            passed=win_concentration >= benchmark_config["field_win_concentration_min"]["target"],
            error=win_concentration - benchmark_config["field_win_concentration_min"]["target"]
        )
        report.checks.append(check)

    return report


def _check_metric(
    metric_name: str,
    simulated_value: float,
    benchmark_spec: Dict
) -> ValidationCheck:
    """
    Check a single metric against its benchmark.

    Args:
        metric_name: Name of the metric
        simulated_value: Simulated value from diagnostics
        benchmark_spec: Benchmark specification dict

    Returns:
        ValidationCheck object
    """
    target = benchmark_spec.get("target")
    target_range = benchmark_spec.get("range")
    units = benchmark_spec.get("units", "")
    description = benchmark_spec.get("description", "")

    # Determine pass/fail
    if target_range:
        passed = target_range[0] <= simulated_value <= target_range[1]
        # Calculate error from nearest boundary
        if simulated_value < target_range[0]:
            error = simulated_value - target_range[0]
        elif simulated_value > target_range[1]:
            error = simulated_value - target_range[1]
        else:
            error = 0.0
    else:
        # Point target - never truly passes, but we track error
        passed = False
        error = simulated_value - target if target else 0.0

    # Calculate percentage error if target exists and is non-zero
    error_pct = None
    if target and target != 0:
        error_pct = (error / abs(target)) * 100

    return ValidationCheck(
        metric_name=metric_name,
        simulated_value=simulated_value,
        target_value=target,
        target_range=target_range,
        units=units,
        description=description,
        passed=passed,
        error=error,
        error_pct=error_pct
    )


def print_validation_report(report: ValidationReport) -> None:
    """
    Print validation report to console.

    Args:
        report: ValidationReport to print
    """
    print("\n" + "=" * 100)
    print(f"Validation Report: {report.tournament_name} vs {report.benchmark_name}")
    print(f"Simulations: {report.num_simulations:,}")
    print("=" * 100)

    # Overall summary
    print(f"\nOverall Result: {report.num_passed}/{len(report.checks)} checks passed ({report.pass_rate:.1f}%)")

    # Detailed results
    print("\n" + "-" * 100)
    print(f"{'Metric':<30} {'Simulated':>12} {'Target':>12} {'Range':>20} {'Status':>8} {'Error':>12}")
    print("-" * 100)

    for check in report.checks:
        # Format target/range
        if check.target_range:
            target_str = f"{check.target_value:.1f}" if check.target_value else "N/A"
            range_str = f"[{check.target_range[0]:.1f}, {check.target_range[1]:.1f}]"
        else:
            target_str = f"{check.target_value:.1f}" if check.target_value else "N/A"
            range_str = "N/A"

        # Format error
        if check.error_pct is not None:
            error_str = f"{check.error:+.2f} ({check.error_pct:+.1f}%)"
        else:
            error_str = f"{check.error:+.2f}"

        print(f"{check.metric_name:<30} {check.simulated_value:>12.2f} {target_str:>12} {range_str:>20} {check.status:>8} {error_str:>12}")

    # Worst misses
    print("\n" + "-" * 100)
    print("Worst Misses (prioritize for tuning):")
    print("-" * 100)

    worst = report.get_worst_misses(5)
    if worst:
        for i, check in enumerate(worst, 1):
            direction = check.error_direction
            print(f"{i}. {check.metric_name}: {check.simulated_value:.2f} {check.units} ({direction})")
            print(f"   Target: {check.target_value:.1f}, Error: {check.error:+.2f} ({check.error_pct:+.1f}%)")
    else:
        print("  (No significant misses)")

    # Tuning recommendations
    print("\n" + "-" * 100)
    print("Tuning Recommendations:")
    print("-" * 100)

    failed_checks = [c for c in report.checks if not c.passed]
    if not failed_checks:
        print("  All checks passed! Model is well-calibrated.")
    else:
        # Group by category
        scoring_issues = [c for c in failed_checks if c.metric_name in ["winning_score", "field_avg", "cut_line"]]
        dist_issues = [c for c in failed_checks if "rate" in c.metric_name]

        if scoring_issues:
            print("\n  Scoring Level Issues:")
            for check in scoring_issues:
                if check.error > 0:
                    print(f"    - {check.metric_name} too high: reduce difficulty or increase player skill")
                else:
                    print(f"    - {check.metric_name} too low: increase difficulty or reduce player skill")

        if dist_issues:
            print("\n  Score Distribution Issues:")
            for check in dist_issues:
                if check.error > 0:
                    print(f"    - {check.metric_name} too high: adjust hole outcome probabilities")
                else:
                    print(f"    - {check.metric_name} too low: adjust hole outcome probabilities")

    print("\n" + "=" * 100)


def export_validation_report(report: ValidationReport, export_dir: str) -> None:
    """
    Export validation report to CSV and text files.

    Args:
        report: ValidationReport to export
        export_dir: Directory to write export files
    """
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)

    # Export CSV
    csv_path = export_path / "validation_summary.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "metric_name",
            "simulated_value",
            "target_value",
            "target_range_min",
            "target_range_max",
            "units",
            "status",
            "error",
            "error_pct",
            "description"
        ])

        for check in report.checks:
            range_min = check.target_range[0] if check.target_range else ""
            range_max = check.target_range[1] if check.target_range else ""

            writer.writerow([
                check.metric_name,
                f"{check.simulated_value:.4f}",
                f"{check.target_value:.4f}" if check.target_value else "",
                f"{range_min:.4f}" if range_min != "" else "",
                f"{range_max:.4f}" if range_max != "" else "",
                check.units,
                check.status,
                f"{check.error:.4f}",
                f"{check.error_pct:.2f}" if check.error_pct is not None else "",
                check.description
            ])

    print(f"\nValidation CSV exported: {csv_path}")

    # Export text report
    txt_path = export_path / "validation_report.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Validation Report\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(f"Tournament: {report.tournament_name}\n")
        f.write(f"Benchmark: {report.benchmark_name}\n")
        f.write(f"Simulations: {report.num_simulations:,}\n\n")
        f.write(f"Overall Result: {report.num_passed}/{len(report.checks)} checks passed ({report.pass_rate:.1f}%)\n\n")

        f.write(f"Detailed Results:\n")
        f.write(f"{'-' * 80}\n")
        for check in report.checks:
            f.write(f"\n{check.metric_name}:\n")
            f.write(f"  Simulated: {check.simulated_value:.2f} {check.units}\n")
            if check.target_value:
                f.write(f"  Target: {check.target_value:.2f} {check.units}\n")
            if check.target_range:
                f.write(f"  Range: [{check.target_range[0]:.2f}, {check.target_range[1]:.2f}]\n")
            f.write(f"  Status: {check.status}\n")
            f.write(f"  Error: {check.error:+.2f}")
            if check.error_pct is not None:
                f.write(f" ({check.error_pct:+.1f}%)")
            f.write(f"\n  Direction: {check.error_direction}\n")

        f.write(f"\n\nWorst Misses:\n")
        f.write(f"{'-' * 80}\n")
        worst = report.get_worst_misses(5)
        for i, check in enumerate(worst, 1):
            f.write(f"{i}. {check.metric_name}: {check.simulated_value:.2f} {check.units} ({check.error_direction})\n")
            f.write(f"   Error: {check.error:+.2f} ({check.error_pct:+.1f}%)\n")

    print(f"Validation report exported: {txt_path}")

    # Export JSON (optional)
    json_path = export_path / "validation_report.json"
    json_data = {
        "tournament": report.tournament_name,
        "benchmark": report.benchmark_name,
        "num_simulations": report.num_simulations,
        "num_passed": report.num_passed,
        "num_failed": report.num_failed,
        "pass_rate": report.pass_rate,
        "checks": [
            {
                "metric_name": c.metric_name,
                "simulated_value": c.simulated_value,
                "target_value": c.target_value,
                "target_range": c.target_range,
                "units": c.units,
                "description": c.description,
                "status": c.status,
                "error": c.error,
                "error_pct": c.error_pct,
                "error_direction": c.error_direction
            }
            for c in report.checks
        ]
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)

    print(f"Validation JSON exported: {json_path}")
