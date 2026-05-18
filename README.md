# Statistical Process Control (SPC) with Time Series Analytics

This project demonstrates Statistical Process Control using control charts to identify out-of-control processes in time series data.

## Business context

Statistical Process Control (SPC) is a method used to monitor and control processes to ensure they operate at their full potential.

Statistical Process Control is an analytical approach to quality management that helps detect and prevent issues in real-time.

The value here is in distinguishing between normal fluctuations and significant deviations. SPC serves as an early warning system, allowing organizations to maintain optimal process performance while minimizing waste and inefficiency.

## Article

Medium article: [Statistical Process Control with Time Series Analytics](https://medium.com/@kylejones_47003/statistical-process-control-spc-with-time-series-analytics-a65b06661dc2)

## Project Structure

```
.
├── README.md           # This file
├── main.py            # Main entry point
├── config.yaml        # Configuration file
├── requirements.txt   # Python dependencies
├── src/               # Core functions
│   ├── core.py        # SPC functions
│   └── plotting.py    # Tufte-style plotting utilities
├── tests/             # Unit tests
├── data/              # Data files (if needed)
└── images/            # Generated plots and figures
```

## Configuration

Edit `config.yaml` to customize:
- Data generation parameters (date range, mean, std)
- Control limits (sigma multiplier, default 3.0)
- Output settings

## Caveats

- By default, the script generates synthetic process data with known out-of-control periods.
- Control limits are calculated using ±3σ (standard deviation) from the mean.
- Points outside control limits are flagged as out-of-control.

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).