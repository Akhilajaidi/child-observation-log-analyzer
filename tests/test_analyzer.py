import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import analyzer  # noqa: E402

CSV_TEXT = """child_name,date,area,notes
Asha,2026-09-01,Math,rods
Asha,2026-09-20,Math,beads
Asha,2026-09-02,Language,letters
Ravi,2026-09-25,Sensorial,tower
Ravi,not-a-date,Math,oops
,2026-09-25,Math,no name
Ravi,2026-09-25,Gardening,unknown area
"""


def make_csv(tmp_path):
    p = tmp_path / "obs.csv"
    p.write_text(CSV_TEXT, encoding="utf-8")
    return p


def test_load_skips_bad_rows(tmp_path):
    obs, skipped = analyzer.load_observations(make_csv(tmp_path))
    assert len(obs) == 4
    assert len(skipped) == 3


def test_counts(tmp_path):
    obs, _ = analyzer.load_observations(make_csv(tmp_path))
    counts = analyzer.count_by_child_area(obs)
    assert counts["Asha"]["Math"] == 2
    assert counts["Asha"]["Sensorial"] == 0  # zero-filled


def test_last_observed_picks_latest(tmp_path):
    obs, _ = analyzer.load_observations(make_csv(tmp_path))
    last = analyzer.last_observed(obs)
    assert last["Asha"]["Math"] == date(2026, 9, 20)


def test_gap_detection(tmp_path):
    obs, _ = analyzer.load_observations(make_csv(tmp_path))
    gaps = analyzer.find_gaps(analyzer.last_observed(obs), date(2026, 9, 25), 14)
    asha = dict(gaps["Asha"])
    assert asha["Language"] == 23      # 2026-09-02 -> 09-25
    assert "Math" not in asha          # seen 5 days ago
    assert asha["Sensorial"] is None   # never observed


def test_missing_column_raises(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("name,when\nA,B\n", encoding="utf-8")
    try:
        analyzer.load_observations(p)
        assert False, "should have raised"
    except ValueError as e:
        assert "child_name" in str(e)


def test_end_to_end(tmp_path):
    out = tmp_path / "out"
    code = analyzer.main(["-i", str(make_csv(tmp_path)), "-o", str(out)])
    assert code == 0
    assert (out / "asha_report.txt").exists()
    assert (out / "class_summary.csv").exists()
