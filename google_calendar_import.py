import datetime
import os
import pytz
import json
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed output, INFO or WARNING for less verbosity
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Google Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google_calendar():
    """Authenticate and return the Google Calendar service."""
    creds = None
    if os.path.exists('token.json'):
        logging.debug("Loading credentials from token.json.")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        logging.debug("token.json not found. User authentication required.")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing expired credentials.")
            creds.refresh(Request())
        else:
            logging.info("Initiating new authentication flow.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
            logging.debug("New credentials saved to token.json.")

    service = build('calendar', 'v3', credentials=creds)
    logging.debug("Google Calendar service built successfully.")
    return service

def get_latest_shift_data(export_dir):
    """Retrieve the latest shift data file."""
    logging.debug(f"Accessing shift data in directory: {export_dir}")
    try:
        files = [os.path.join(export_dir, f) for f in os.listdir(export_dir)]
        latest_file = max(files, key=os.path.getctime)
        logging.info(f"Latest shift data file found: {latest_file}")
    except ValueError:
        logging.error("No shift data files found in the directory.")
        raise FileNotFoundError("No shift data files found in the Exported_shifts directory.")

    with open(latest_file, 'r') as f:
        shift_data = json.load(f)
        logging.debug("Shift data loaded successfully.")

    # Clean up old files if necessary
    if len(files) > 8:
        files.sort(key=os.path.getctime)
        old_files = files[:-4]
        for file_path in old_files:
            os.remove(file_path)
            logging.info(f"Deleted old shift file: {file_path}")

    return shift_data

def delete_events_in_current_month(service, calendar_id, timezone):
    """Delete all events in the current month."""
    now = datetime.datetime.now(timezone)
    current_year = now.year
    current_month = now.month

    # Define the time range for the current month
    time_min = timezone.localize(datetime.datetime(current_year, current_month, 1))
    if current_month == 12:
        next_month = datetime.datetime(current_year + 1, 1, 1)
    else:
        next_month = datetime.datetime(current_year, current_month + 1, 1)
    time_max = timezone.localize(next_month)

    logging.debug(f"Deleting events between {time_min.isoformat()} and {time_max.isoformat()}")

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    logging.info(f"Found {len(events)} events to delete.")

    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
        logging.debug(f"Deleted event: {event['summary']} (ID: {event['id']})")

def add_shifts_to_calendar(service, calendar_id, shift_data, timezone):
    """Add shifts to the Google Calendar."""
    now = datetime.datetime.now(timezone)
    current_year = now.year
    current_month = now.month

    for shift in shift_data:
        shift_date = shift.get('date')
        shift_time = shift.get('time')
        logging.debug(f"Processing shift on {shift_date} at {shift_time}")

        if '-' in shift_time:
            try:
                start_time_str, end_time_str = [t.strip() for t in shift_time.split('-')]

                start_datetime = datetime.datetime.strptime(
                    f"{current_year}-{current_month:02d}-{shift_date} {start_time_str}",
                    "%Y-%m-%d %H:%M"
                )
                end_datetime = datetime.datetime.strptime(
                    f"{current_year}-{current_month:02d}-{shift_date} {end_time_str}",
                    "%Y-%m-%d %H:%M"
                )

                start_datetime = timezone.localize(start_datetime)
                end_datetime = timezone.localize(end_datetime)

                event_body = {
                    'summary': 'Směna McDonalds',
                    'location': 'McDonalds Globus Liberec, Sousedská 611',
                    'colorId': '5',
                    'start': {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'Europe/Prague',
                    },
                    'end': {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'Europe/Prague',
                    },
                }

                event_result = service.events().insert(calendarId=calendar_id, body=event_body).execute()
                logging.info(f"Created event: {event_result['summary']} on {shift_date}")
            except Exception as e:
                logging.error(f"Error creating event for shift on {shift_date}: {e}")
        else:
            logging.warning(f"Invalid time format for shift on {shift_date}: {shift_time}")

def main():
    logging.info("Shift synchronization script started.")
    try:
        service = authenticate_google_calendar()

        # Paths and configurations
        export_dir = os.path.join(os.path.dirname(__file__), "Exported_shifts")
        shift_data = get_latest_shift_data(export_dir)

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            logging.debug("Configuration loaded.")
        calendar_id = config.get('calendar_id')

        if not calendar_id:
            logging.error("Calendar ID not found in config.json.")
            raise ValueError("Calendar ID is missing in config.json.")

        timezone = pytz.timezone('Europe/Prague')

        # Delete events and add new shifts
        delete_events_in_current_month(service, calendar_id, timezone)
        add_shifts_to_calendar(service, calendar_id, shift_data, timezone)

        logging.info("Shift synchronization completed successfully.")
    except Exception as e:
        logging.exception("An unexpected error occurred.")
    finally:
        logging.info("Script execution finished.")

if __name__ == "__main__":
    main()
