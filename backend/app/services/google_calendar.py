import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.core.config import settings

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.creds = None
        self.service = None
        # Robust path finding: Get the directory of THIS file (app/services), go up two levels to 'backend'
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.token_path = os.path.join(base_dir, 'token.json')
        self.creds_path = os.path.join(base_dir, 'credentials.json')

    def authenticate(self):
        """Authenticates the user and creates/refreshes tokens."""
        if os.path.exists(self.token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                print(f"Error loading token.json: {e}")
                self.creds = None

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                     print(f"Error refreshing token: {e}")
                     self.creds = None
            
            if not self.creds:
                if not os.path.exists(self.creds_path):
                    print(f"WARNING: {self.creds_path} not found. Calendar integration disabled.")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                    # Use a local server flow (requires port forwarding for headless)
                    # Or run this once locally and copy token.json
                    self.creds = flow.run_local_server(port=0) 
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return False

            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
        except Exception as e:
             print(f"Failed to build service: {e}")
             return False

    def create_event(self, summary: str, start_time: datetime.datetime, end_time: datetime.datetime, attendee_email: str = None):
        """Creates an event in the primary calendar."""
        if not self.service:
            if not self.authenticate():
                return None

        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata', # Configurable
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }

        if attendee_email:
            event['attendees'] = [{'email': attendee_email}]

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return event.get('htmlLink')
        except Exception as e:
            print(f"An error occurred creating calendar event: {e}")
            return None

calendar_service = CalendarService()
