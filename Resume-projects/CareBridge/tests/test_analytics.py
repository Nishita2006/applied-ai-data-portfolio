import pandas as pd
from src.analytics import preparation_score, status_counts


def test_preparation_score_uses_numpy_and_excludes_na():
    frame = pd.DataFrame({"status": ["complete", "not_started", "not_applicable"]})
    assert preparation_score(frame) == 50


def test_status_counts_uses_pandas_grouping():
    result = status_counts(pd.DataFrame({"status": ["complete", "complete", "in_progress"]}))
    assert result.loc[result.status == "complete", "tasks"].iloc[0] == 2

