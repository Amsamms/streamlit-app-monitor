import requests
import time
from datetime import datetime
import logging
from typing import List, Dict
import concurrent.futures
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_monitor.log'),
        logging.StreamHandler()
    ]
)

class StreamlitAppMonitor:
    def __init__(self, urls: List[str]):
        self.urls = urls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.wake_up_wait = 120  # 2 minutes wait after wake-up attempt
        self.sleep_patterns = [
            "zzz. this app has gone to sleep",
            "app has gone to sleep due to inactivity",
            "yes, get this app back up!"
        ]
        self.app_health_status = {url: {'wake_up_attempts': 0, 'last_status': 'unknown', 'last_check': None} for url in urls}

    def log_health_status(self, url: str, status: str, details: str, response_time: float = None):
        """Log detailed health status for an app."""
        current_time = datetime.now()
        self.app_health_status[url]['last_status'] = status
        self.app_health_status[url]['last_check'] = current_time

        health_log = f"Health Status for {url}:\n"
        health_log += f"  Status: {status}\n"
        health_log += f"  Details: {details}\n"
        if response_time is not None:
            health_log += f"  Response Time: {response_time:.2f}s\n"
        health_log += f"  Last Check: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        health_log += f"  Total Wake-up Attempts: {self.app_health_status[url]['wake_up_attempts']}\n"
        health_log += "  " + "="*50

        if status == 'active':
            logging.info(health_log)
        elif status == 'sleeping':
            logging.warning(health_log)
        else:
            logging.error(health_log)

    def is_sleeping(self, response_text: str) -> bool:
        """Check if the app is in sleeping state based on Streamlit's sleeping page content."""
        response_text = response_text.lower()
        return any(pattern in response_text for pattern in self.sleep_patterns)

    def verify_app_active(self, url: str, max_checks: int = 6) -> bool:
        """Verify if the app has become active after wake-up attempt."""
        for check in range(max_checks):
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200 and not self.is_sleeping(response.text):
                    logging.info(f"App {url} verified as active after {check + 1} checks")
                    return True
                logging.info(f"App {url} still not active, check {check + 1}/{max_checks}")
                time.sleep(20)  # Wait 20 seconds between checks
            except Exception as e:
                logging.warning(f"Error verifying app status for {url}: {str(e)}")
                time.sleep(20)
        logging.warning(f"App {url} failed to become active after {max_checks} checks")
        return False

    def wake_up_app(self, url: str) -> bool:
        """Attempt to wake up a sleeping app by simulating the wake-up button click."""
        self.app_health_status[url]['wake_up_attempts'] += 1
        logging.info(f"Attempting to wake up {url} (Attempt #{self.app_health_status[url]['wake_up_attempts']})")
        
        try:
            # First get the sleeping page
            response = self.session.get(url, timeout=10)
            if not self.is_sleeping(response.text):
                logging.info(f"App {url} is not sleeping, no wake-up needed")
                return False

            # Parse the HTML to find the wake-up button
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the wake-up button by looking for common button patterns
            wake_button = None
            for button in soup.find_all(['button', 'a']):
                if any(text in button.get_text().lower() for text in ['wake up', 'get back up', 'restart']):
                    wake_button = button
                    break

            if wake_button:
                # Extract the button's action URL or form data
                if wake_button.get('href'):
                    wake_url = wake_button['href']
                    if not wake_url.startswith('http'):
                        wake_url = url.rstrip('/') + wake_url
                    wake_response = self.session.get(wake_url, timeout=10)
                    if wake_response.status_code == 200:
                        logging.info(f"Wake-up request sent to {url}, waiting for app to start...")
                        return True
                elif wake_button.get('onclick'):
                    # Handle onclick JavaScript events if needed
                    logging.info(f"Found wake-up button with onclick event for {url}")
                    return True

            logging.warning(f"Could not find wake-up button for {url}")
            return False

        except Exception as e:
            logging.error(f"Error attempting to wake up {url}: {str(e)}")
            return False

    def check_app_status(self, url: str) -> Dict:
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    # Check if the app is sleeping using Streamlit's sleeping page patterns
                    if self.is_sleeping(response.text):
                        logging.warning(f"Attempt {attempt + 1}: {url} is sleeping (Streamlit sleep state detected)")
                        if attempt < self.max_retries - 1:
                            # Try to wake up the app
                            if self.wake_up_app(url):
                                logging.info(f"Wake-up request sent to {url}, waiting {self.wake_up_wait} seconds...")
                                time.sleep(self.wake_up_wait)  # Wait for initial wake-up
                                
                                # Verify if the app has become active
                                if self.verify_app_active(url):
                                    logging.info(f"Successfully woke up {url}")
                                    result = {
                                        'url': url,
                                        'status': 'active',
                                        'response_time': response.elapsed.total_seconds(),
                                        'details': 'App was successfully woken up'
                                    }
                                    self.log_health_status(url, 'active', 'App was successfully woken up', response.elapsed.total_seconds())
                                    return result
                                else:
                                    logging.warning(f"App {url} did not become active after wake-up attempt")
                                    time.sleep(self.retry_delay)
                                    continue
                            else:
                                logging.warning(f"Failed to wake up {url}")
                                time.sleep(self.retry_delay)
                                continue
                        result = {
                            'url': url,
                            'status': 'sleeping',
                            'response_time': response.elapsed.total_seconds(),
                            'details': 'App is in Streamlit sleep state'
                        }
                        self.log_health_status(url, 'sleeping', 'App is in Streamlit sleep state', response.elapsed.total_seconds())
                        return result
                    result = {
                        'url': url,
                        'status': 'active',
                        'response_time': response.elapsed.total_seconds(),
                        'details': 'App is running normally'
                    }
                    self.log_health_status(url, 'active', 'App is running normally', response.elapsed.total_seconds())
                    return result
                elif response.status_code == 503:
                    logging.warning(f"Attempt {attempt + 1}: {url} is temporarily unavailable (503)")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    result = {
                        'url': url,
                        'status': 'unavailable',
                        'response_time': None,
                        'details': 'Service temporarily unavailable'
                    }
                    self.log_health_status(url, 'unavailable', 'Service temporarily unavailable')
                    return result
                else:
                    logging.warning(f"Attempt {attempt + 1}: {url} returned status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1}: Error accessing {url}: {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        result = {
            'url': url,
            'status': 'inactive',
            'response_time': None,
            'details': 'App is not responding after multiple attempts'
        }
        self.log_health_status(url, 'inactive', 'App is not responding after multiple attempts')
        return result

    def monitor_apps(self):
        cycle_count = 0
        while True:
            cycle_count += 1
            logging.info(f"Starting monitoring cycle #{cycle_count}")
            print("\n" + "="*50)
            print(f"Monitoring cycle #{cycle_count} started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50 + "\n")

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {executor.submit(self.check_app_status, url): url for url in self.urls}
                
                for future in concurrent.futures.as_completed(future_to_url):
                    result = future.result()
                    url = result['url']
                    status = result['status']
                    response_time = result['response_time']
                    details = result['details']
                    
                    if status == 'active':
                        print(f"✅ {url}")
                        print(f"   Status: Active (Response time: {response_time:.2f}s)")
                    elif status == 'sleeping':
                        print(f"😴 {url}")
                        print(f"   Status: Sleeping (Attempting to wake up)")
                        print(f"   Details: {details}")
                        print(f"   Wake-up Attempts: {self.app_health_status[url]['wake_up_attempts']}")
                    elif status == 'unavailable':
                        print(f"⚠️ {url}")
                        print(f"   Status: Temporarily Unavailable")
                        print(f"   Details: {details}")
                    else:
                        print(f"❌ {url}")
                        print(f"   Status: Inactive")
                        print(f"   Details: {details}")

            print("\n" + "="*50)
            print(f"Cycle #{cycle_count} completed. Waiting for next cycle...")
            print("="*50 + "\n")
            time.sleep(300)  # Wait 5 minutes before next cycle

def main():
    urls = [
        "https://amsamms-scatter-plotter-scatter-plotter-f4ojyj.streamlit.app/",
        "https://amsamms-general-machine-learning-algorithm-main-rs6nt9.streamlit.app/",
        "https://datasetanalysis-0.streamlit.app/",
        "https://pdf-table-extract.streamlit.app/",
        "https://images-table-extractor.streamlit.app/",
        "https://unit-converter-engineering.streamlit.app/",
        "https://gas-density-calculator-r.streamlit.app/",
        "https://envelopplotter.streamlit.app/",
        "https://liquid-control-valves-eval.streamlit.app/",
        "https://gas-control-valves-evaluation.streamlit.app/",
        "https://sabri-gpt-chatbot.streamlit.app/",
        "https://assistant-api-sabri.streamlit.app/",
        "https://movie-retriever.streamlit.app/",
        "https://h2-prediction.streamlit.app/"
    ]

    monitor = StreamlitAppMonitor(urls)
    try:
        monitor.monitor_apps()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        logging.info("Monitoring stopped by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 