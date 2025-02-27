import os
import json
import logging
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import subprocess
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """
    Loads the configuration from config.json in the user's home directory.
    """
    config_path = Path.home() / "config.json"
    if not config_path.exists():
        logging.error(f"Configuration file not found at {config_path}")
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with config_path.open('r') as config_file:
        config = json.load(config_file)
    return config

def initialize_driver(chrome_path):
    """
    Initializes the Chrome WebDriver with the specified Chrome executable path.
    """
    options = Options()
    options.binary_location = chrome_path
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver, username, password):
    """
    Logs into the website using the provided credentials.
    """
    driver.get('https://mymcd.eu/login/')
    wait = WebDriverWait(driver, 10)

    # Wait for the username field to be present and enter credentials
    username_input = wait.until(EC.presence_of_element_located((By.ID, 'username')))
    password_input = driver.find_element(By.ID, 'password')
    login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

def navigate_to_shifts_page(driver, shift_page_url):
    """
    Navigates to the shifts page after logging in. time
    """
    driver.get(shift_page_url)
    # Wait until specific element is present to ensure page is loaded
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'MuiGrid-item')))

def extract_shift_data(page_source):
    """
    Extracts shift data from the page source using BeautifulSoup.
    """
    shifts = []
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find all shift items
    shift_items = soup.find_all('div', class_='MuiGrid-item')
    
    for shift in shift_items:
        # Extract date from h2 tag
        date_element = shift.find('h2')
        date = date_element.text.strip() if date_element else 'N/A'
        if not date.isdigit():
            date = 'N/A'
            
        # Extract time
        time_element = shift.find('span', class_='MuiTypography-body2')
        time_text = time_element.text.strip() if time_element else 'N/A'
        if time_text and all(char.isdigit() or char in [':', ' ', '-'] for char in time_text):
            time_value = time_text
        else:
            time_value = 'N/A'

        if date != 'N/A' and time_value != 'N/A':
            shifts.append({'date': date, 'time': time_value})
    
    # Debug information
    logging.info(f"Found {len(shifts)} shifts")
    
    return shifts

def save_shift_data(shifts):
    """
    Saves the extracted shift data to a JSON file in the Exported_shifts directory.
    """
    # Generate the filename with current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exported_shifts_{current_time}.json"

    # Define the directory path for exported shifts
    export_dir = Path(__file__).parent / "Exported_shifts"
    export_dir.mkdir(exist_ok=True)

    # Save the extracted shift data to the file in the Exported_shifts folder
    file_path = export_dir / filename
    with file_path.open('w') as file:
        json.dump(shifts, file)

    logging.info(f"Shift data saved to file: {file_path}")
def main():
    try:
        config = load_config()
        shift_page_url = config['shift_page_url']
        username = config['username']
        password = config['password']
        chrome_path = config['chrome_path']

        driver = initialize_driver(chrome_path)
        login(driver, username, password)
        navigate_to_shifts_page(driver, shift_page_url)

        # Get the page source after the shifts page is loaded
        page_source = driver.page_source

        # Close the browser
        driver.quit()

        # Extract shift data
        shifts = extract_shift_data(page_source)

        # Save shift data
        save_shift_data(shifts)

        # Output the extracted shift data
        for shift in shifts:
            print(shift)

        # Run google_calendar_import.py script in the same folder
        '''script_path = Path(__file__).parent / "google_calendar_import.py"
        if script_path.exists():
            logging.info("Running google_calendar_import.py script...")
            subprocess.run(['python', str(script_path)], check=True)
        else:
            logging.error(f"Script {script_path} not found.")'''

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
