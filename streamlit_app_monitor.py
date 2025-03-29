import time
from datetime import datetime
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def log_status(url: str, status: str):
    """Log only the essential information: timestamp, URL, and status."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('streamlit_monitor.log', 'a') as f:
        f.write(f"{timestamp} | {url} | {status}\n")

class StreamlitAppMonitor:
    def __init__(self, urls: List[str]):
        self.urls = urls
        self.wake_up_wait = 120  # 2 minutes wait after wake-up attempt

    def is_sleeping(self, driver) -> bool:
        """Check if the app is in sleeping state using Selenium."""
        try:
            wake_up_button_xpath = "//button[contains(., 'get this app back up')]"
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, wake_up_button_xpath))
            )
            return True
        except TimeoutException:
            return False
        except Exception:
            return False

    def wake_up_app(self, url: str, driver) -> bool:
        """Attempt to wake up a sleeping app using Selenium."""
        try:
            wake_up_button_xpath = "//button[contains(., 'get this app back up')]"
            wake_up_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, wake_up_button_xpath))
            )
            wake_up_button.click()
            time.sleep(self.wake_up_wait)  # Wait for app to wake up
            return True
        except Exception:
            return False

    def check_app_status(self, url: str) -> Dict:
        driver = None
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("window-size=1920x1080")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            is_sleeping = self.is_sleeping(driver)
            
            if is_sleeping:
                if self.wake_up_app(url, driver):
                    return {
                        'url': url,
                        'status': 'ACTIVATED',
                        'details': 'App was sleeping and has been activated'
                    }
                else:
                    return {
                        'url': url,
                        'status': 'ERROR',
                        'details': 'Failed to wake up sleeping app'
                    }
            else:
                return {
                    'url': url,
                    'status': 'ACTIVE',
                    'details': 'App is already active'
                }
                
        except Exception as e:
            return {
                'url': url,
                'status': 'ERROR',
                'details': f'Error: {str(e)}'
            }
        finally:
            if driver:
                driver.quit()

    def monitor_apps(self):
        print(f"\nChecking apps at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        for url in self.urls:
            result = self.check_app_status(url)
            status_emoji = {
                'ACTIVE': '✅',
                'ACTIVATED': '🔄',
                'ERROR': '❌'
            }
            print(f"{status_emoji.get(result['status'], '❓')} {url}")
            print(f"   Status: {result['status']}")
            print(f"   Details: {result['details']}")
            print("-"*50)
            
            # Log only essential information
            log_status(result['url'], result['status'])

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
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main() 