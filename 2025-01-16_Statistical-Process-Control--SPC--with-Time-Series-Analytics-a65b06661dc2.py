# Description: Short example for Statistical Process Control SPC with Time Series Analytics.

# Generate simulated process data

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    np.random.seed(42)
    time = pd.date_range(start="2023-01-01", periods=100, freq="D")
    values = np.random.normal(50, 2, 100)
    # Introduce out-of-control points
    values[30:35] += 8
    values[70:75] -= 8
    # Create a DataFrame
    df = pd.DataFrame({"Time": time, "Value": values})

    # Calculate control limits
    mean = df["Value"].mean()
    std_dev = df["Value"].std()
    ucl = mean + 3 * std_dev  # Upper Control Limit
    lcl = mean - 3 * std_dev  # Lower Control Limit
    # Plot the control chart
    plt.figure(figsize=(12, 6))
    plt.plot(df["Time"], df["Value"], label="Process Data", marker="o", linestyle="-")
    plt.axhline(mean, color="blue", linestyle="--", label="Mean")
    plt.axhline(ucl, color="red", linestyle="--", label="Upper Control Limit (UCL)")
    plt.axhline(lcl, color="red", linestyle="--", label="Lower Control Limit (LCL)")
    # Highlight out-of-control points
    out_of_control = (df["Value"] > ucl) | (df["Value"] < lcl)
    plt.scatter(
        df["Time"][out_of_control],
        df["Value"][out_of_control],
        color="red",
        label="Out of Control",
    )
    # Shade out-of-control regions
    plt.fill_between(
        df["Time"],
        ucl,
        lcl,
        where=(df["Value"] > ucl) | (df["Value"] < lcl),
        color="red",
        alpha=0.1,
    )
    # Add labels and legend
    plt.title("Control Chart with Out-of-Control Areas")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
