# Changelog

## v1.1 - Usability & Analysis Improvements (2026-03-30)

### New Features

**Large Demo Field**
- Added `data/demo/players/large_field_demo.csv` with 90 players
- Provides realistic Masters-sized field for testing
- All players calibrated within validation constraints

**Analysis Utilities**
- New `src/analysis/analyze.py` module for inspecting simulation results
- Command-line interface for common analyses:
  - `summary`: Quick overview of simulation results
  - `winners`: Top winning probabilities
  - `cuts`: Cut-making likelihood analysis
  - `scores`: Field score distribution statistics
  - `finishes`: Finish position distribution
  - `compare`: Side-by-side player comparison
- Usage: `python -m src.analysis.analyze outputs/summary.csv --command <command>`

**Enhanced CSV Exports**
- Added `export_sim_results_csv()` for per-simulation detail exports
- Added `export_finish_distribution_csv()` for enhanced finish statistics
- Functions available in `src/outputs/export_csv.py`

**Improved Documentation**
- Enhanced README with:
  - Installation instructions
  - Complete workflow examples
  - Analysis utilities documentation
  - Detailed output file descriptions
  - Project status and roadmap
- Added output file format documentation
- Added complete end-to-end workflow example

### Changes

**Demo Data**
- Fixed validation constraints in all demo CSV files
- Ensured all par skill values within allowed ranges:
  - `par3_skill`: -2 to 2
  - `par4_skill`: -2 to 2
  - `par5_skill`: -3 to 3

**Documentation Structure**
- Reorganized README sections for better flow
- Added "Project Status" section
- Expanded "Future Development" with categorized roadmap
- Added "Output Files" section with detailed descriptions

### Files Added

- `data/demo/players/large_field_demo.csv` - 90-player demo field
- `src/analysis/__init__.py` - Analysis module init
- `src/analysis/analyze.py` - Analysis CLI and utilities
- `CHANGELOG.md` - This file

### Files Modified

- `README.md` - Comprehensive documentation updates
- `src/outputs/export_csv.py` - Added new export functions
- `data/demo/players/large_field_demo.csv` - Validation fixes

### Workflow Improvements

Users can now:
1. Run simulations with realistic field sizes
2. Export results to multiple CSV formats
3. Analyze results using command-line utilities
4. Inspect distributions without writing custom code
5. Follow documented end-to-end workflows

### Technical Notes

- No changes to core simulation engine or scoring model
- All improvements focused on usability and analysis
- Maintained zero external dependencies (Python stdlib only)
- All CSV exports compatible with standard spreadsheet tools

---

## v1.0 - Initial Calibrated Release

- Core Monte Carlo simulation engine
- Tournament, round, and cut logic
- Hole-level probabilistic scoring
- Player skill profiles with par-specific adjustments
- CSV data adapter system
- Basic console output and CSV export
- Diagnostic collection and reporting
