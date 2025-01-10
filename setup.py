import os
import subprocess
import getpass
import json

# Function to install dependencies
print("Installing dependencies...")
def install_dependencies():
    try:
        subprocess.check_call(["pip", "install", "selenium", "beautifulsoup4", "ics", "webdriver_manager", "google-auth-oauthlib", "google-auth-httplib2", "google-api-python-client", "tzlocal", "pytz"])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing dependencies: {e}")
        exit(1)

# Install dependencies
install_dependencies()

# Now we can safely import the required libraries
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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

# Prompt user for input
shift_page_url = input("Please enter the URL of the shift page: ").strip()
while not shift_page_url:
    shift_page_url = input("The shift page URL cannot be blank. Please enter the URL of the shift page: ").strip()

username = input("Please enter your username: ").strip()
while not username:
    username = input("The username cannot be blank. Please enter your username: ").strip()

password = getpass.getpass("Please enter your password: ").strip()
while not password:
    password = getpass.getpass("The password cannot be blank. Please enter your password: ").strip()
    
# Check if credentials.json exists in the script's directory

    script_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(script_dir, "credentials.json")
    if not os.path.exists(credentials_path):
        print(f"Error: {credentials_path} does not exist. Please create the file with your credentials.")
        exit(1)

# Import the required libraries for the rest of the script 
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle
import pytz
import tzlocal

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


# Function to list upcoming events on the user's calendar
def main():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # List all calendars
    print("Fetching all calendars:")
    calendar_list = service.calendarList().list().execute().get('items', [])
    
    if not calendar_list:
        print("No calendars found.")
        exit(1)
    
    print("Please choose a calendar:")
    for i, calendar in enumerate(calendar_list):
        print(f"{i + 1}. {calendar['summary']}")
    
    choice = input("Enter the number of the calendar you want to use: ").strip()
    while not choice.isdigit() or int(choice) < 1 or int(choice) > len(calendar_list):
        choice = input("Invalid choice. Please enter a valid number: ").strip()
    
    chosen_calendar = calendar_list[int(choice) - 1]
    print(f"You have chosen: {chosen_calendar['summary']}")
    print(f"{len(calendar_list) + 1}. Create a new calendar")

    choice = input("Enter the number of the calendar you want to use: ").strip()
    while not choice.isdigit() or int(choice) < 1 or int(choice) > len(calendar_list) + 1:
        choice = input("Invalid choice. Please enter a valid number: ").strip()

    if int(choice) == len(calendar_list) + 1:
        new_calendar_name = input("Enter the name for the new calendar: ").strip()
        while not new_calendar_name:
            new_calendar_name = input("The calendar name cannot be blank. Please enter the name for the new calendar: ").strip()

        new_calendar = {
            'summary': new_calendar_name,
            'timeZone': pytz.timezone('America/Los_Angeles').zone
        }
        local_timezone = tzlocal.get_localzone()
        new_calendar = {
            'summary': new_calendar_name,
            'timeZone': local_timezone.zone
        }

        created_calendar = service.calendars().insert(body=new_calendar).execute()
        print(f"Created calendar: {created_calendar['id']}")
        chosen_calendar = created_calendar
    else:
        chosen_calendar = calendar_list[int(choice) - 1]
        print(f"You have chosen: {chosen_calendar['summary']}")

   
if __name__ == '__main__':
    chosen_calendar = main()


# Download WebDriver and find Chrome path
driver_path = download_chromedriver()
chrome_path = find_chrome_path()

# Define script_dir as the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define safe destination for config.json
safe_destination = os.path.join(script_dir, "config.json")

# Save the user inputs and paths to a configuration file
config = {
    "shift_page_url": shift_page_url,
    "username": username,
    "password": password,
    "driver_path": driver_path,
    "chrome_path": chrome_path,
    "calendar_id": chosen_calendar['id']
}

# Write the configuration to a file
with open(safe_destination, 'w') as config_file:
    json.dump(config, config_file)

print(f"Configuration saved to {safe_destination}")
