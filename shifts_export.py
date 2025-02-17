import os
import json
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

# Define safe destination for config.json
safe_destination = os.path.join(os.path.expanduser("~"), "config.json")

# Load configuration from the file
with open(safe_destination, 'r') as config_file:
    config = json.load(config_file)

shift_page_url = config['shift_page_url']
username = config['username']
password = config['password']
chrome_path = config['chrome_path']

# Setup Chrome options
options = Options()
options.binary_location = chrome_path

# Initialize Chrome driver (ChromeDriver) using webdriver_manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Login using Selenium
driver.get('https://mymcd.eu/login/')

# Locate the input fields and login button
username_input = driver.find_element(By.ID, 'username')
password_input = driver.find_element(By.ID, 'password')
login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')

# Enter login credentials and log in
username_input.send_keys(username)
password_input.send_keys(password)
login_button.click()

# Wait for the page to load
time.sleep(3)  # Wait for 3 seconds

# Navigate to the shifts page
driver.get(shift_page_url)

# Wait for dynamic content to load
time.sleep(4)  # Wait for 4 seconds

# Extract the HTML source of the page after loading
page_source = driver.page_source

# Close the browser
driver.quit()

# Use BeautifulSoup to parse the HTML
soup = BeautifulSoup(page_source, 'html.parser')

# Locate and extract shift data and dates from the month
shifts = []
shift_elements = soup.find_all('div', class_='MuiGrid-item')
for shift in shift_elements:
    date_element = shift.find('h2').text if shift.find('h2') else 'N/A'
    if date_element and date_element.strip().isdigit():
        date = date_element.strip()
    else:
        date = 'N/A'

    time_element = shift.find('span', class_='MuiTypography-body2').text if shift.find('span', class_='MuiTypography-body2') else 'N/A'
    if time_element and all(char.isdigit() or char == ':' or char == ' ' or char == '-' for char in time_element.strip()):
        time = time_element.strip()
    else:
        time = 'N/A'

    if date != 'N/A' and time != 'N/A':
        shifts.append({'date': date, 'time': time})

# Save the extracted shift data to a temporary file
# Generate the filename with current date and time
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"exported_shifts_{current_time}.json"

# Define the directory path for exported shifts
export_dir = os.path.join(os.path.dirname(__file__), "Exported_shifts")

# Create the directory if it does not exist
if not os.path.exists(export_dir):
    os.makedirs(export_dir)

# Save the extracted shift data to the file in the Exported_shifts folder
file_path = os.path.join(export_dir, filename)
with open(file_path, 'w') as file:
    json.dump(shifts, file)

temp_file_path = file_path

print(f"Shift data saved to file: {temp_file_path}")

# Output the extracted shift data
for shift in shifts:
    print(shift)
