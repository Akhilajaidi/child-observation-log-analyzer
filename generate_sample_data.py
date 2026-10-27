"""Generate a made-up observation log so the project can be shown publicly.

All names, dates and notes are fictional. No real children's data is used.
Run:  python generate_sample_data.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # same data every run, so results are reproducible

CHILDREN = ["Aarav", "Diya", "Kabir", "Meera", "Rohan", "Sana", "Vihaan", "Zoya"]
AREAS = ["Practical Life", "Sensorial", "Language", "Math"]

NOTES = {
    "Practical Life": ["Pouring water with focus", "Buttoning frame, repeated 3 times", "Table washing"],
    "Sensorial": ["Pink tower, built independently", "Matching sound cylinders", "Colour tablets sorting"],
    "Language": ["Sandpaper letters, traced 's'", "Moveable alphabet words", "Sound game with objects"],
    "Math": ["Number rods 1-5", "Spindle box counting", "Golden beads introduction"],
}

# Deliberate gaps so the "needs attention" flag has something to find:
# child -> (area, last date they were observed in that area)
GAPS = {
    "Diya": ("Math", date(2026, 9, 7)),
    "Kabir": ("Language", date(2026, 9, 14)),
    "Rohan": ("Sensorial", date(2026, 9, 1)),
    "Zoya": ("Practical Life", date(2026, 9, 10)),
}

START = date(2026, 9, 1)
END = date(2026, 10, 9)


def weekdays(start, end):
    day = start
    while day <= end:
        if day.weekday() < 5:  # Monday-Friday only
            yield day
        day += timedelta(days=1)


def main():
    rows = []
    for day in weekdays(START, END):
        for child in CHILDREN:
            if random.random() < 0.9:  # not every child is observed every day
                area = random.choice(AREAS)
                gap = GAPS.get(child)
                if gap and area == gap[0] and day > gap[1]:
                    continue  # skip: creates the planned gap
                rows.append([child, day.isoformat(), area, random.choice(NOTES[area])])

    out = Path("data/sample_observations.csv")
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["child_name", "date", "area", "notes"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} made-up observations to {out}")


if __name__ == "__main__":
    main()
