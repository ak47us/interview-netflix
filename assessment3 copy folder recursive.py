#!/usr/local/bin/python3

from __future__ import print_function
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


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


def copyFolder(service, sourceFolderID, destinationFolderID):
    results         = []
    morePages       = True
    nextPageToken   = None
    filesCount      = 0
    dirsCount       = 0
    # Pagination
    while morePages == True:
            # Get folder contents:
            response = service.files().list(q="'" + sourceFolderID + "' in parents",
                                            spaces='drive',
                                            fields='*',
                                            pageToken=nextPageToken
                                                ).execute()
            
            # Process folder's children:
            for i in response.get('files'):
                
                # Duplicate a file;
                if i.get('mimeType') != 'application/vnd.google-apps.folder':
                    file_metadata = i.get('metadata')
                    file_metadata = [file_metadata].append("{'parents': '" + destinationFolderID + " '}")
                    service.files().copy(fileId=i.get('id'), body={'name': i.get('name'),
                                                                    'parents': [destinationFolderID],
                                                                    }).execute() 
                else: # Create a new folder:
                    newFolder = service.files().create(body={'name': i.get('name'),
                                                    'parents':  [destinationFolderID],
                                                    'mimeType': 'application/vnd.google-apps.folder'
                                                    }).execute()


                if i.get('mimeType') == 'application/vnd.google-apps.folder':
                    copyFolder(service, i.get('id'), newFolder.get('id'))
                    #print(i.get("name") + ' total: ' + str(len(results)))
            
            # Next page:
            if response.get("nextPageToken"):
                nextPageToken = response.get("nextPageToken")
                morePages = True
            else:
                morePages = False

    return



def main():
    print("This script copies the content of the source folder to the destination folder.")
    service = checkAuth()
    copyFolder(service, "1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V", "1Go10vfKpKU1fuTuqXHJ0oIyix29181Ga") # Netflix's source folder

if __name__ == '__main__':
    main()