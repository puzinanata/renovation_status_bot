import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# Load Environment
load_dotenv()

class DataManager:
    """Handles Git-safe persistence of status data."""
    def __init__(self, folder="data", filename="status_cache.json"):
        self.path = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        
    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def print_log(message):
    """Standardized logging with timestamps."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def normalize(text):
    """Cleans up text for reliable comparison."""
    if not text: return ""
    return " ".join(text.replace("\xa0", " ").split())

def send_notification(message):
    """Dispatches Telegram alerts."""
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
    except Exception as e:
        print_log(f"Notification error: {e}")

def get_driver():
    """Builds a resilient headless browser."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Masking as a real browser to prevent blocks
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def check_aima():
    # 1. Initialize State
    dm = DataManager()
    cache = dm.load()
    
    # 2. Get Accounts from .env
    accounts = []
    i = 1
    while os.getenv(f"ACCOUNT_{i}_EMAIL"):
        accounts.append({
            "email": os.getenv(f"ACCOUNT_{i}_EMAIL"),
            "pass": os.getenv(f"ACCOUNT_{i}_PASS")
        })
        i += 1

    driver = get_driver()
    wait = WebDriverWait(driver, 20)

    try:
        for acc in accounts:
            email = acc["email"]
            print_log(f"Starting check: {email}")
            
            driver.get("https://services.aima.gov.pt/RAR/login.php")
            
            # Auth Phase
            wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)
            driver.find_element(By.ID, "password").send_keys(acc["pass"])
            driver.find_element(By.XPATH, "//*[@id='login_form']/div/div[2]/div/button[2]").click()
            
            # Scrape Phase
            status_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "td[style*='background-color: salmon']")))
            raw_status = status_el.text.strip()
            
            # Logic: Compare Normalized, Store Raw
            if normalize(raw_status) != normalize(cache.get(email)):
                print_log(f"CHANGE DETECTED for {email}")
                send_notification(f"Status Updated for {email}:\n\n{raw_status}")
                cache[email] = raw_status # Update memory
            else:
                print_log(f"No change for {email}")

    except Exception as e:
        print_log(f"Critical error: {e}")
    finally:
        driver.quit()
        dm.save(cache) 
        print_log("Check completed.")

if __name__ == "__main__":
    check_aima()