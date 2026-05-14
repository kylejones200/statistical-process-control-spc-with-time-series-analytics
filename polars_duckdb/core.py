"""Statistical Process Control using Polars and DuckDB.

calculate_control_limits + identify_out_of_control collapse into a single
DuckDB query: global AVG/STDDEV_SAMP compute the limits; CASE WHEN flags
every point in the same pass — no second DataFrame scan needed.
"""

import duckdb
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
from pathlib import Path
from typing import Dict


def generate_process_data(
    start_date: str = "2023-01-01",
    periods:    int   = 100,
    freq:       str   = "D",
    mean:       float = 50.0,
    std:        float = 2.0,
    seed:       int   = 42,
) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    step  = timedelta(days=1) if freq == "D" else timedelta(hours=1)
    dates = [start + step * i for i in range(periods)]
    values = rng.normal(mean, std, periods)
    values[30:35] += 8   # deliberate out-of-control spike
    values[70:75] -= 8
    return pl.DataFrame({"Time": dates, "Value": values.tolist()})


def calculate_control_limits(
    df: pl.DataFrame,
    sigma_multiplier: float = 3.0,
) -> Dict[str, float]:
    """Global mean and ±3σ limits via DuckDB aggregates."""
    return duckdb.sql(f"""
        SELECT
            AVG(Value)                                      AS mean,
            STDDEV_SAMP(Value)                              AS std_dev,
            AVG(Value) + {sigma_multiplier} * STDDEV_SAMP(Value) AS ucl,
            AVG(Value) - {sigma_multiplier} * STDDEV_SAMP(Value) AS lcl
        FROM df
    """).pl().row(0, named=True)


def add_control_flags(
    df: pl.DataFrame,
    sigma_multiplier: float = 3.0,
) -> pl.DataFrame:
    """Single DuckDB query: compute limits AND flag out-of-control points."""
    return duckdb.sql(f"""
        WITH stats AS (
            SELECT
                AVG(Value)                                           AS mean,
                AVG(Value) + {sigma_multiplier} * STDDEV_SAMP(Value) AS ucl,
                AVG(Value) - {sigma_multiplier} * STDDEV_SAMP(Value) AS lcl
            FROM df
        )
        SELECT
            d.Time,
            d.Value,
            s.mean,
            s.ucl,
            s.lcl,
            CASE WHEN d.Value > s.ucl OR d.Value < s.lcl THEN 1 ELSE 0 END AS out_of_control
        FROM df d, stats s
        ORDER BY d.Time
    """).pl()


def plot_control_chart(
    df: pl.DataFrame,
    output_path: Path,
    plot: bool = False,
):
    if not plot:
        return
    times   = df["Time"].to_list()
    values  = df["Value"].to_list()
    mean    = df["mean"][0]
    ucl     = df["ucl"][0]
    lcl     = df["lcl"][0]
    ooc_mask = [v == 1 for v in df["out_of_control"].to_list()]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(times, values, label="Process Data", color="#4A90A4",
            linewidth=1.2, marker="o", markersize=3)
    ax.axhline(mean, color="#8B6F9E", linestyle="--", linewidth=1.2, label="Mean")
    ax.axhline(ucl,  color="#D4A574", linestyle="--", linewidth=1.2, label="UCL")
    ax.axhline(lcl,  color="#D4A574", linestyle="--", linewidth=1.2, label="LCL")

    ooc_times  = [t for t, m in zip(times,  ooc_mask) if m]
    ooc_values = [v for v, m in zip(values, ooc_mask) if m]
    if ooc_times:
        ax.scatter(ooc_times, ooc_values, color="#D4A574", s=50,
                   label="Out of Control", zorder=5)

    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend(loc="best", ncol=2)
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()
