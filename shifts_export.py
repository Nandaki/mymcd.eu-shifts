import os
import json
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Define safe destination for config.json
safe_destination = os.path.join(os.path.expanduser("~"), "config.json")

# Load configuration from the file
with open(safe_destination, 'r') as config_file:
    config = json.load(config_file)

shift_page_url = config['shift_page_url']
username = config['username']
password = config['password']
driver_path = config['driver_path']
chrome_path = config['chrome_path']

# Create Chrome service instance
service = Service(driver_path)

# Setup Chrome options
options = webdriver.ChromeOptions()
options.binary_location = chrome_path

# Initialize Chrome driver (ChromeDriver)
driver = webdriver.Chrome(service=service, options=options)

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
time.sleep(2)  # Wait for 2 seconds

# Navigate to the shifts page
driver.get(shift_page_url)

# Wait for dynamic content to load
time.sleep(3)  # Wait for 3 seconds

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
    if date_element: 
        date_text = date_element.strip() 
        date = date_text if date_text.isdigit() else 'N/A'
    else:
        date = 'N/A'

    time = shift.find('span', class_='MuiTypography-body2').text if shift.find('span', class_='MuiTypography-body2') else 'N/A'
    if date != 'N/A' and time != 'N/A': 
        shifts.append({'date': date, 'time': time}) 

# Save the extracted shift data to a temporary file
with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json', dir=tempfile.gettempdir()) as temp_file:
    json.dump(shifts, temp_file)
    temp_file_path = temp_file.name

print(f"Shift data saved to temporary file: {temp_file_path}")

# Output the extracted shift data
for shift in shifts:
    print(shift)
