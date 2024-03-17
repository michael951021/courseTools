import datetime
import os.path

from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

'''
Takes in the name of the course, task, and the date (in MM DD YYYY format) we would like to 
make the task due, and invokes Task API to add it online.
RETURNS a boolean of whether it successfully added the task to the calendar
'''
def calendize(course,name,month,day,year):
    try:
        # Load credentials from a file or any other storage mechanism
        SCOPES = ['https://www.googleapis.com/auth/tasks']
        creds = None  # Update with your credentials file path
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", scopes=SCOPES)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", scopes=SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        # Create a Google Calendar service object
        service = build('tasks', 'v1', credentials=creds)

        # Define the event details
        date = str(year)+"-"+str(month)+"-"+str(day)+"T00:00:00Z"
        task = {
            'title': name,
            'notes': course,
            'due': date,
        }

        # Insert the event into the calendar
        event = service.tasks().insert(tasklist='@default', body=task).execute()
        return True
    except:
        return False
if __name__ == "__main__":
    #Example case
    calendize("1400","hw 3","03","24","2024")