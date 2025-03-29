# Streamlit App Monitor

A Python script to monitor the status of Streamlit applications and detect when they go to sleep.

## Features

- Monitors multiple Streamlit apps concurrently
- Detects when apps are sleeping
- Attempts to wake up sleeping apps
- Logs status and errors
- Runs via GitHub Actions every 11 hours

## Requirements

- Python 3.12+
- Chrome/Chromium browser
- Selenium WebDriver
- Required Python packages (see requirements.txt)

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

The script can be run in two ways:

1. **Manual Run**:
```bash
python streamlit_app_monitor.py
```

2. **GitHub Actions**:
- The script runs automatically every 11 hours via GitHub Actions
- You can also trigger manual runs from the Actions tab
- Logs are saved as artifacts in each run

## Configuration

The list of URLs to monitor can be configured in two ways:

1. **Environment Variable**:
```bash
export STREAMLIT_URLS="https://app1.streamlit.app,https://app2.streamlit.app"
```

2. **Default List**:
If no environment variable is set, the script uses a default list of URLs.

## Logging

The script logs:
- App status (active/inactive)
- Sleep detection
- Wake-up attempts
- Errors and exceptions

Logs are saved to `streamlit_monitor.log` and are available as artifacts in GitHub Actions runs.

## GitHub Actions

The workflow:
1. Runs every 11 hours
2. Sets up Python and Chrome
3. Installs dependencies
4. Runs the monitor script
5. Saves logs as artifacts

## License

MIT License 