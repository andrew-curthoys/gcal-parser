import datetime
from dateutil import parser
import os.path
import traceback
import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

with open('config.yaml', 'r') as f:
  CONFIG = yaml.safe_load(f)

SHIFT_DICT = CONFIG['shift_dict']


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting all upcoming events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=2500,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      try:
        if 'QGenda' not in event['description']:
          continue
      except KeyError:
        continue
      try:
        shift_name = event["summary"]
        original_shift_name = shift_name.split(':')[-1]
        shift_datetime = parser.parse(event['start']['dateTime'])
        shift_time = shift_datetime.strftime('%-I%p')
        new_shift_name = f"{shift_time}:{original_shift_name}"
        event['summary'] = new_shift_name
        updated_event = (
            service.events()
            .update(
                calendarId='primary',
                eventId=event['id'],
                body=event
            )
            .execute()
        )
        print(f"Updated event {updated_event['summary']}")
      except:
        print(f"Error updating shift on {shift_datetime.strftime('%Y-%m-%d %H')}")
        print(f"Error details: {traceback.format_exc}")

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()