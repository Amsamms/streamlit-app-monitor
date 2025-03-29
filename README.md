# Streamlit App Monitor

A Python script to monitor and automatically wake up sleeping Streamlit apps deployed on Streamlit Community Cloud.

## Features

- Monitors multiple Streamlit apps simultaneously
- Automatically detects sleeping apps
- Attempts to wake up sleeping apps
- Tracks health status and wake-up attempts
- Detailed logging of app status and response times
- Concurrent monitoring with configurable intervals

## Requirements

- Python 3.6+
- requests
- beautifulsoup4

## Installation

1. Clone the repository:
```bash
git clone https://github.com/amsamms/streamlit-app-monitor.git
cd streamlit-app-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Edit the `urls` list in `main()` to include your Streamlit app URLs.

2. Run the script:
```bash
python streamlit_app_monitor.py
```

The script will:
- Monitor all specified apps every 5 minutes
- Attempt to wake up any sleeping apps
- Log all activities to `streamlit_monitor.log`
- Display real-time status in the console

## Configuration

You can modify these parameters in the `StreamlitAppMonitor` class:
- `max_retries`: Number of retry attempts (default: 3)
- `retry_delay`: Delay between retries in seconds (default: 5)
- `wake_up_wait`: Wait time after wake-up attempt in seconds (default: 120)
- Monitoring interval: Time between monitoring cycles (default: 300 seconds)

## Logging

The script creates a `streamlit_monitor.log` file that contains:
- Health status for each app
- Wake-up attempts and results
- Response times
- Error messages
- Timestamps for all events

## License

MIT License 