import datetime
import os
import pytz
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
    creds = None   

    # Load configuration from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    calendar_id = config.get('calendar_id')

    # Load credentials from token.json
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no valid credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Define the path to the shift data file
    export_dir = os.path.join(os.path.dirname(__file__), "Exported_shifts")
    
    # Get the newest file from the directory
    list_of_files = os.listdir(export_dir)
    full_path = [os.path.join(export_dir, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getctime)

    # Read the exported shift data file
    with open(latest_file, 'r') as file:
        shift_data = json.load(file)

    # If there are more than 8 files, delete the oldest 3
    if len(list_of_files) > 8:
        oldest_files = sorted(full_path, key=os.path.getctime)[:3]
        for file in oldest_files:
            os.remove(file)

    local_tz = pytz.timezone('Europe/Prague')
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    calendar_id = 'primary'  # Replace with your calendar ID if not using the primary calendar

    for shift in shift_data:
        if '-' in shift['time']:
            start_time_str = f"{current_year}-{current_month:02d}-{shift['date']} {shift['time'].split('-')[0].strip()}"
            end_time_str = f"{current_year}-{current_month:02d}-{shift['date']} {shift['time'].split('-')[1].strip()}"
            try:
                start_time = local_tz.localize(datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")).isoformat()
                end_time = local_tz.localize(datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")).isoformat()
                print(f"Start time: {start_time}, End time: {end_time}")

                event = {
                    'summary': 'Směna McDonalds',
                    'location': 'McDonalds Globus Liberec, Sousedská 611',
                    'colorId': '5',
                    'start': {
                        'dateTime': start_time,
                        'timeZone': 'Europe/Prague',
                    },
                    'end': {
                        'dateTime': end_time,
                        'timeZone': 'Europe/Prague',
                    },
                }
                created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
                print(f"Created event: {created_event['id']}")
            except ValueError as e:
                print(f"Error parsing date/time for shift on {shift['date']}: {e}")
        else:
            print(f"Invalid time format for shift on {shift['date']}: {shift['time']}")

if __name__ == "__main__":
    main()
