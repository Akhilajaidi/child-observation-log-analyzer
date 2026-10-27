# Child Observation Log Analyzer

A command-line tool, built with plain Python, that turns a daily Montessori observation log (CSV) into per-child reports and flags areas that haven't been observed recently.

> **All data in this repo is made up.** No real children's records are used or should ever be committed.

## Why I built it

In a classroom, teachers record daily observations across areas like Practical Life, Sensorial, Language and Math. Spotting which child hasn't been observed in an area for a while means scrolling through spreadsheets. This tool does it in one command.

## What it does

1. Counts observations per child, per area
2. Flags any area with no observation for **14+ days** (configurable) or never observed
3. Writes one `.txt` report per child plus a class-wide `class_summary.csv`
4. Skips malformed rows (bad date, missing name, unknown area) and tells you which ones

## Project structure

```
child-observation-log-analyzer/
├── analyzer.py               # main program (reading, analysis, writing, CLI)
├── generate_sample_data.py   # creates fictional sample data
├── data/sample_observations.csv
├── reports/                  # example output
├── tests/test_analyzer.py    # pytest tests
├── requirements.txt
└── README.md
```

## Quick start

```bash
git clone https://github.com/<your-username>/child-observation-log-analyzer.git
cd child-observation-log-analyzer
python generate_sample_data.py     # optional: regenerate sample data
python analyzer.py                 # uses data/sample_observations.csv
```

### Options

| Option | Meaning | Default |
|---|---|---|
| `-i`, `--input` | input CSV | `data/sample_observations.csv` |
| `-o`, `--output-dir` | where reports go | `reports` |
| `-t`, `--threshold-days` | days without observation before flagging | `14` |
| `--as-of YYYY-MM-DD` | compare against this date | latest date in the CSV |

Example: `python analyzer.py -i my_log.csv -t 10 --as-of 2026-10-09`

## Input format

```csv
child_name,date,area,notes
Diya,2026-09-01,Language,"Sandpaper letters, traced 's'"
```

`area` must be one of: Practical Life, Sensorial, Language, Math. Dates use `YYYY-MM-DD`.

## Example output (`reports/diya_report.txt`)

```
OBSERVATION REPORT - Diya
As of: 2026-10-09
============================================

Area             Count   Last observed
--------------------------------------------
Practical Life       5   2026-10-07
Sensorial            7   2026-10-08
Language             5   2026-09-21
Math                 0   never

Total observations: 17

NEEDS ATTENTION (no observation for 14+ days):
  * Language: 18 days ago
  * Math: never observed
```

## Run the tests

```bash
pip install -r requirements.txt
pytest
```

## Python concepts practiced

File reading/writing, `csv.DictReader`/`csv.writer`, dictionaries and `defaultdict`, loops, `datetime`, `pathlib`, `argparse`, error handling, and unit testing with `pytest`.

## Ideas for next steps

- Export reports to Excel (`openpyxl`)
- Add a weekly-trend chart (`matplotlib`)
- Support custom area lists via a config file

## License

MIT
