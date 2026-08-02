from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.figure import Figure


def preparation_score(tasks: pd.DataFrame) -> int:
    applicable = tasks.loc[tasks["status"] != "not_applicable"]
    if applicable.empty:
        return 0
    completed = np.count_nonzero(applicable["status"].to_numpy() == "complete")
    return int(np.rint(completed / len(applicable) * 100))


def symptom_chart(symptoms: pd.DataFrame) -> Figure:
    frame = symptoms.copy()
    frame["onset_date"] = pd.to_datetime(frame["onset_date"])
    frame = frame.sort_values("onset_date")
    fig = Figure(figsize=(8, 3.4), facecolor="#fbfaf6")
    axis = fig.subplots()
    colors = ["#277b73", "#3e6f91", "#b87932"]
    axis.bar(frame["symptom"], frame["severity"], color=colors[: len(frame)])
    axis.set_ylim(0, 10)
    axis.set_ylabel("Patient-rated severity (0–10)")
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", alpha=.18)
    fig.tight_layout()
    return fig


def status_counts(tasks: pd.DataFrame) -> pd.DataFrame:
    return (tasks.groupby("status", as_index=False).size().rename(columns={"size": "tasks"}))

