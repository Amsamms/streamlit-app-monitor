import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

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
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-infobars")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("--disable-popup-blocking")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use ChromeDriverManager with specific version for stability
        self.service = Service(ChromeDriverManager(version="114.0.5735.90").install())
        
    def get_urls(self):
        """Get URLs from environment variable or use default list"""
        urls_str = os.getenv('STREAMLIT_URLS')
        if urls_str:
            return [url.strip() for url in urls_str.split(',')]
        
        # Default list of URLs to monitor
        return [
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

    def is_sleeping(self, driver):
        """Check if the app is sleeping by looking for the wake-up button"""
        try:
            # Wait for potential wake-up button with various selectors
            wake_up_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                    "//button[contains(text(), 'Wake up') or contains(text(), 'wake up') or contains(text(), 'Wake Up') or contains(text(), 'WAKE UP')]"
                ))
            )
            return True
        except TimeoutException:
            return False

    def wake_up_app(self, driver):
        """Attempt to wake up the app by clicking the wake-up button"""
        try:
            # Wait for wake-up button to be clickable
            wake_up_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(text(), 'Wake up') or contains(text(), 'wake up') or contains(text(), 'Wake Up') or contains(text(), 'WAKE UP')]"
                ))
            )
            wake_up_button.click()
            time.sleep(5)  # Wait for wake-up process
            return True
        except Exception as e:
            logging.error(f"Failed to wake up app: {str(e)}")
            return False

    def check_app_status(self, url):
        """Check the status of a single Streamlit app"""
        driver = None
        try:
            driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            driver.get(url)
            
            # Wait for the main Streamlit app to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "stApp"))
            )
            
            # Check if app is sleeping
            if self.is_sleeping(driver):
                logging.info(f"App is sleeping: {url}")
                if self.wake_up_app(driver):
                    logging.info(f"Successfully woke up app: {url}")
                else:
                    logging.error(f"Failed to wake up app: {url}")
            else:
                logging.info(f"App is active: {url}")
                
        except TimeoutException:
            logging.error(f"Timeout while checking app: {url}")
        except WebDriverException as e:
            logging.error(f"Error checking app {url}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error checking app {url}: {str(e)}")
        finally:
            if driver:
                driver.quit()

    def monitor_apps(self):
        """Monitor all Streamlit apps concurrently"""
        urls = self.get_urls()
        logging.info(f"Starting monitoring of {len(urls)} apps")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.check_app_status, urls)
        
        logging.info("Monitoring completed")

def main():
    monitor = StreamlitAppMonitor()
    monitor.monitor_apps()

if __name__ == "__main__":
    main() 