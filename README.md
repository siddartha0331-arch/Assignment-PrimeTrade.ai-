# MLOps Engineering Task - Trading Signal Pipeline

This project processes cryptocurrency OHLCV data to calculate rolling means and generate trading signals. It outputs structured metrics in JSON format.

## Setup Instructions

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

That's it! You should be good to go.

## Local Execution Instructions

To run the script locally, use:

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

Make sure your `data.csv` file has a `close` column, otherwise the script will throw an error. The config file needs `seed`, `window`, and `version` fields.

## Docker Instructions

If you want to run this in Docker:

Build the image:
```bash
docker build -t mlops-task .
```

Then run it:
```bash
docker run --rm mlops-task
```

The Dockerfile copies the necessary files (data.csv, config.yaml) into the container, so make sure they exist in your project directory before building.

## Expected Output

When everything works correctly, you'll get a `metrics.json` file that looks like this:

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4990,
  "latency_ms": 127,
  "seed": 42,
  "status": "success"
}
```

If something goes wrong, you'll see an error output instead:

```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Description of what went wrong"
}
```

The error message should tell you what happened - usually it's a missing file or invalid config.

## Dependencies

You'll need these Python packages (they're in `requirements.txt`):

- **pandas** - for reading and processing CSV files
- **numpy** - used for the random seed and numerical operations
- **pyyaml** - to parse the config.yaml file

## Project Structure

Here's what the project looks like:

```
├── run.py              # Main script
├── config.yaml         # Config with seed, window, version
├── data.csv            # Your input data (needs 'close' column)
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker setup
├── README.md           # This file
├── metrics.json        # Output file (generated after running)
└── run.log            # Log file (generated after running)
```

## How It Works

The script does the following:

1. Loads the config from `config.yaml` (seed, window size, version)
2. Reads the CSV file and checks that it has the required columns
3. Calculates a rolling mean using the window size from config
4. Generates signals: 1 if close price > rolling mean, 0 otherwise
5. Calculates the signal rate (average of all signals) and how long it took
6. Writes everything to `metrics.json` and logs to `run.log`

The random seed ensures you get the same results if you run it multiple times with the same data and config.

## Notes

- The script uses `yaml.safe_load()` to read the config, so make sure your YAML is valid
- Logs are written to both the log file and console
- If the CSV is empty or missing the 'close' column, you'll get a clear error message
- The latency is measured in milliseconds and includes the entire processing time
