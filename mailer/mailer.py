from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
import pickle
import json
import os.path
import argparse

parser = argparse.ArgumentParser(description="Email to your friends with this simple script")

parser.add_argument("--email", help="Email to send")

args = parser.parse_args()

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDS = ['creds.pickle', 'credentials.json']
TOKENS = json.loads(open("../credentials.json").read())

def create_message(sender, to, subject, msg="hi"):
  message = MIMEText(
    "<b>{}</b>".format(msg),
    "html"
  )
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode("utf-8")}

def send_message(service, email, message):
  try:
    message = (service.users().messages().send(userId=email, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except Exception as error:
    print('An error occurred: %s' % error)

def main():
    if args.email is None:
      exit()
    creds = None

    if os.path.exists(CREDS[0]):
        with open(CREDS[0], 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS[1], SCOPES, redirect_uri="https://developers.google.com/oauthplayground")
            creds = flow.run_local_server(port=5000)

        with open(CREDS[0], 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message = create_message(args.email, "test@test.com", "Test Email")
    send_message(service, args.email, message)

if __name__ == '__main__':
    main()