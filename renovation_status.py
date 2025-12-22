import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# Credentials
load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

ACCOUNTS = [
    {"email": os.getenv("ACCOUNT_1_EMAIL"),
     "password": os.getenv("ACCOUNT_1_PASS"),
     "status": "Estado do Processo\nO seu processo está a aguardar a decisão por parte da AIMA."
     },
    {"email": os.getenv("ACCOUNT_2_EMAIL"),
     "password": os.getenv("ACCOUNT_2_PASS"),
     "status": "Estado do Processo\nA audiência prévia foi concluída e o processo está a ser analisado com base na informação que foi recolhida."
     },
]

def send_telegram_notification(chat_id, bot_token, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

def normalize(text):
    return " ".join(text.replace("\xa0", " ").split())

def print_log(time_log, message):
    print(f"{time_log.strftime('%Y-%m-%d %H:%M:%S')} - {message}")


def build_driver():
    """Start Chrome with retries and return (driver, wait)."""
    chrome_options = Options()
    # this line is needed to run in my laptop
    # chrome_options.add_argument("--incognito")

    # these lines are needed in both cases
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # these lines are needed to run in server (Lesha's laptop)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    print_log(time_log=datetime.now(), message="!!!Start - call driver chrome")

    return driver, wait
        

def check_account(account):
    driver, wait = build_driver()
    try:
        # Step 1: Open site
        driver.get("https://services.aima.gov.pt/RAR/login.php")
        wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        print_log(time_log=datetime.now(), message="Open site")

        # Step 2: Authorization
        username_input = driver.find_element(By.NAME, "email")
        username_input.send_keys(account["email"])

        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(account["password"])

        login_button = driver.find_element(By.XPATH, "//*[@id='login_form']/div/div[2]/div/button[2]")
        login_button.click()
        print_log(time_log=datetime.now(), message=f"Authorization for {account['email']}")

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "td[style*='background-color: salmon']")))
        print_log(time_log=datetime.now(), message=f"Login completed for {account['email']}")

        # Step 3: Check status
        status_cell = driver.find_element(By.CSS_SELECTOR, "td[style*='background-color: salmon']")
        status_text = status_cell.text.strip()
        print_log(time_log=datetime.now(), message=f"Status found for {account['email']}: {status_text}")

        message = f"{account['email']} status changed:\n{status_text}"

        if normalize(status_text) != normalize(account["status"]):
            send_telegram_notification(chat_id, bot_token, message)
            print_log(time_log=datetime.now(), message=f"Notification sent for {account['email']}")

        print_log(time_log=datetime.now(), message=f"Status check completed for {account['email']}")

    except Exception as e:
        send_telegram_notification(chat_id, bot_token, message=f"Check your account {account['email']}, unknown status occurred.")
        print_log(time_log=datetime.now(), message=f"Status check completed for {account['email']}, with error: {e}")
    finally:
        driver.quit()

def run_checks():
    for account in ACCOUNTS:
        check_account(account)


if __name__ == "__main__":
    run_checks()
    print_log(time_log=datetime.now(), message="!!!Final - call function run_checks")
