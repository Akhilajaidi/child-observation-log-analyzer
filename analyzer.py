"""Child Observation Log Analyzer
================================
Reads a CSV of daily Montessori observations and:
  1. counts observations per child per area
  2. flags areas a child has not been observed in for N+ days (default 14)
  3. writes one report per child, plus a class-wide summary CSV

Expected CSV columns: child_name, date (YYYY-MM-DD), area, notes
Uses only the Python standard library.
"""

import argparse
import csv
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

AREAS = ["Practical Life", "Sensorial", "Language", "Math"]
REQUIRED_COLUMNS = {"child_name", "date", "area"}


# ---------------------------------------------------------------- reading ---
def load_observations(path):
    """Read the CSV and return (valid_rows, skipped_messages).

    Each valid row is a dict: {"child": str, "date": date, "area": str, "notes": str}.
    Bad rows are skipped and described, instead of crashing the whole program.
    """
    observations, skipped = [], []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required column(s): {', '.join(sorted(missing))}")

        for line_no, row in enumerate(reader, start=2):  # line 1 is the header
            child = (row["child_name"] or "").strip()
            area = (row["area"] or "").strip()
            try:
                obs_date = datetime.strptime((row["date"] or "").strip(), "%Y-%m-%d").date()
            except ValueError:
                skipped.append(f"line {line_no}: bad date {row['date']!r}")
                continue
            if not child:
                skipped.append(f"line {line_no}: missing child name")
                continue
            if area not in AREAS:
                skipped.append(f"line {line_no}: unknown area {area!r}")
                continue
            observations.append(
                {"child": child, "date": obs_date, "area": area, "notes": (row.get("notes") or "").strip()}
            )
    return observations, skipped


# --------------------------------------------------------------- analysis ---
def count_by_child_area(observations):
    """{child: {area: count}} - every area is present, even with a 0 count."""
    counts = defaultdict(lambda: {area: 0 for area in AREAS})
    for obs in observations:
        counts[obs["child"]][obs["area"]] += 1
    return dict(counts)


def last_observed(observations):
    """{child: {area: most recent date or None}}."""
    last = defaultdict(lambda: {area: None for area in AREAS})
    for obs in observations:
        current = last[obs["child"]][obs["area"]]
        if current is None or obs["date"] > current:
            last[obs["child"]][obs["area"]] = obs["date"]
    return dict(last)


def find_gaps(last_seen, as_of, threshold_days=14):
    """Return {child: [(area, days_since_or_None), ...]} for areas needing attention.

    days_since is None when the child was never observed in that area.
    """
    gaps = {}
    for child, areas in last_seen.items():
        flagged = []
        for area in AREAS:
            seen = areas[area]
            if seen is None:
                flagged.append((area, None))
            else:
                days = (as_of - seen).days
                if days >= threshold_days:
                    flagged.append((area, days))
        gaps[child] = flagged
    return gaps


# ---------------------------------------------------------------- writing ---
def write_child_report(child, counts, last_seen, gaps, as_of, threshold_days, out_dir):
    """Write a plain-text report for one child and return its path."""
    path = Path(out_dir) / f"{child.lower().replace(' ', '_')}_report.txt"
    lines = [
        f"OBSERVATION REPORT - {child}",
        f"As of: {as_of.isoformat()}",
        "=" * 44,
        "",
        f"{'Area':<16}{'Count':>6}   Last observed",
        "-" * 44,
    ]
    for area in AREAS:
        seen = last_seen[area].isoformat() if last_seen[area] else "never"
        lines.append(f"{area:<16}{counts[area]:>6}   {seen}")
    lines += ["", f"Total observations: {sum(counts.values())}", ""]

    if gaps:
        lines.append(f"NEEDS ATTENTION (no observation for {threshold_days}+ days):")
        for area, days in gaps:
            detail = "never observed" if days is None else f"{days} days ago"
            lines.append(f"  * {area}: {detail}")
    else:
        lines.append("All areas observed recently. Nice coverage!")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_summary_csv(all_counts, all_gaps, out_dir):
    """Write one class-wide CSV: a row per child."""
    path = Path(out_dir) / "class_summary.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["child_name", *AREAS, "total", "areas_needing_attention"])
        for child in sorted(all_counts):
            counts = all_counts[child]
            flagged = "; ".join(area for area, _ in all_gaps[child]) or "none"
            writer.writerow([child, *(counts[a] for a in AREAS), sum(counts.values()), flagged])
    return path


# -------------------------------------------------------------------- CLI ---
def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Analyze a Montessori observation log (CSV).")
    parser.add_argument("-i", "--input", default="data/sample_observations.csv", help="input CSV file")
    parser.add_argument("-o", "--output-dir", default="reports", help="folder for generated reports")
    parser.add_argument("-t", "--threshold-days", type=int, default=14, help="days without observation to flag (default 14)")
    parser.add_argument(
        "--as-of",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        help="compare against this date, YYYY-MM-DD (default: latest date in the CSV)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    observations, skipped = load_observations(args.input)
    if not observations:
        print("No valid observations found. Nothing to report.")
        return 1

    as_of = args.as_of or max(o["date"] for o in observations)
    counts = count_by_child_area(observations)
    last_seen = last_observed(observations)
    gaps = find_gaps(last_seen, as_of, args.threshold_days)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in sorted(counts):
        write_child_report(child, counts[child], last_seen[child], gaps[child], as_of, args.threshold_days, out_dir)
    write_summary_csv(counts, gaps, out_dir)

    flagged_children = sum(1 for g in gaps.values() if g)
    print(f"Read {len(observations)} observations for {len(counts)} children (as of {as_of}).")
    print(f"{flagged_children} child(ren) have at least one area needing attention.")
    print(f"Reports written to: {out_dir}/")
    if skipped:
        print(f"Skipped {len(skipped)} bad row(s):")
        for message in skipped:
            print(f"  - {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
