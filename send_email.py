# Importing libraries
import os, re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import httplib2
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase


SCOPES = 'https://www.googleapis.com/auth/gmail.send'
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CLIENT_SECRET_FILE = 'secret_gmail.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

def get_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secret_gmail.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Call the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    return service

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"

def send_email(mail_subject, mail_content, img_attach=[], receiver_address='daniel.wandarti@objective.com.br'):
    mail_content = re.sub(r"<img src=[^>]*><br/>", "", mail_content)
    
    service = get_service()
    sender = 'jirasyncobj@gmail.com'

    msg = MIMEMultipart('mixed')
    msg['Subject'] = mail_subject
    msg['From'] = sender
    msg['To'] = receiver_address
    msg.attach(MIMEText("", 'plain'))
    msg.attach(MIMEText(mail_content, 'html'))

    for attachmentFile in img_attach:
        content_type, encoding = mimetypes.guess_type(attachmentFile)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(attachmentFile, 'r', encoding="UTF-8")
            msg_attach = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(attachmentFile, 'rb')
            msg_attach = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(attachmentFile, 'rb')
            msg_attach = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(attachmentFile, 'rb')
            msg_attach = MIMEBase(main_type, sub_type)
            msg_attach.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(attachmentFile)
        msg_attach.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(msg_attach)

    raw_string = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    message1 = {'raw': raw_string}
    result = SendMessageInternal(service, "me", message1)

    return result
