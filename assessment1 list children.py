#!/usr/local/bin/python3

from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def checkAuth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
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
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        exit()


def getContents(service, folderID):
    results         = []
    morePages       = True
    nextPageToken   = None
    # Pagination
    while morePages == True:
            print("Fetching results...")
            response = service.files().list(q="'" + folderID + "' in parents",
                                            spaces='drive',
                                            fields='*',
                                            pageToken=nextPageToken
                                                ).execute()
            for i in response.get('files'): 
                results = results + [i]
            if response.get("nextPageToken"):
                nextPageToken = response.get("nextPageToken")
                morePages = True
            else:
                morePages = False
    return results



def main():
    dirCount    = 0
    fileCount   = 0
    print("This script generates a report of all files and folders in total for a given Google Drive folder.")
    service = checkAuth()
    list = getContents(service, "1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V") # Netflix's test folder
    print('Number of objects in folder: ' + str(len(list)))
    print('Number of objects in and below folder: ' + str(len(list)))
    for i in list:
        if dict(i).get('mimeType') == 'application/vnd.google-apps.folder':
            dirCount  += 1
        else:
            fileCount += 1
    print('Number of folders: ' + str(dirCount))
    print('Number of files: '   + str(fileCount))

if __name__ == '__main__':
    main()