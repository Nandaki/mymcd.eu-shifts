import os
import subprocess
import getpass
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Function to install dependencies
def install_dependencies():
    subprocess.check_call(["pip", "install", "selenium", "beautifulsoup4", "webdriver_manager"])

# Function to download the ChromeDriver
def download_chromedriver():
    print("Downloading ChromeDriver...")
    driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver downloaded to: {driver_path}")
    return driver_path

# Function to find the Chrome executable path
def find_chrome_path():
    options = Options()
    chrome_path = options.binary_location
    print(f"Chrome executable path: {chrome_path}")
    return chrome_path

# Install dependencies
install_dependencies()

# Prompt user for input
shift_page_url = input("Please enter the URL of the shift page: ").strip()
username = input("Please enter your username: ").strip()
password = getpass.getpass("Please enter your password: ").strip()

# Check if any input is blank
if not shift_page_url or not username or not password:
    raise ValueError("The shift page URL, username, and password cannot be blank.")

# Download WebDriver and find Chrome path
driver_path = download_chromedriver()
chrome_path = find_chrome_path()

# Define safe destination for config.json
safe_destination = os.path.join(os.path.expanduser("~"), "config.json")

# Save the user inputs and paths to a configuration file
config = {
    "shift_page_url": shift_page_url,
    "username": username,
    "password": password,
    "driver_path": driver_path,
    "chrome_path": chrome_path
}

# Write the configuration to a file
import json
with open(safe_destination, 'w') as config_file:
    json.dump(config, config_file)

print(f"Configuration saved to {safe_destination}")
