#!/usr/bin/env python3
"""Statistical Process Control — Polars + DuckDB rewrite."""

import argparse
import logging
from pathlib import Path

import yaml
from core import (
    add_control_flags,
    calculate_control_limits,
    generate_process_data,
    plot_control_chart,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_config(config_path: Path | None = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="SPC — Polars + DuckDB")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path(config["output"]["figures_dir"])
    )
    output_dir.mkdir(exist_ok=True)
    sigma = config["control_limits"]["sigma_multiplier"]
    df = generate_process_data(
        config["data"]["start_date"],
        config["data"]["periods"],
        config["data"]["frequency"],
        config["data"]["mean"],
        config["data"]["std"],
        config["data"]["seed"],
    )
    # limits from DuckDB aggregates
    limits = calculate_control_limits(df, sigma)
    logging.info(f"Control limits (σ×{sigma}):")
    logging.info(f"  Mean : {limits['mean']:.3f}")
    logging.info(f"  UCL  : {limits['ucl']:.3f}")
    logging.info(f"  LCL  : {limits['lcl']:.3f}")
    # flags computed in the same DuckDB pass
    flagged = add_control_flags(df, sigma)
    n_ooc = flagged["out_of_control"].sum()
    logging.info(f"\nOut-of-control points : {n_ooc} / {flagged.height}")
    logging.info(
        f"\n{flagged.filter(flagged['out_of_control'] == 1).select(['Time', 'Value', 'ucl', 'lcl'])}"
    )
    plot_control_chart(flagged, output_dir / "control_chart.png")
    logging.info(f"\nDone. Figures saved to {output_dir}")


if __name__ == "__main__":
    main()
