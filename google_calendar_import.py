import datetime
import os.path
import pickle
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
  SCOPES = ['https://www.googleapis.com/auth/calendar']

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
 

  # Get the current year and month
  current_year = datetime.datetime.now().year
  current_month = datetime.datetime.now().month
  event = {
      'summary': 'Směna',
      'location': 'McDonalds Globus, Sousedská 611, Liberec',
      'description': 'Směna v McDonalds Globus',
      'start': {
          'dateTime': (datetime.utcnow() + timedelta(days=1)).isoformat(),
          'timeZone': 'America/Los_Angeles',
      },
      'end': {
          'dateTime': (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat(),
          'timeZone': 'America/Los_Angeles',
      },
  }

if __name__ == "__main__":
    main()
