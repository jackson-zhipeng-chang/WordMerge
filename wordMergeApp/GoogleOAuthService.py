from __future__ import print_function
import re
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import file, client, tools
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Group

SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]    

def init():
    """Initilization Function, takes SCOPES.
    """
    creds = generateCredentials()
    docService = build('docs', 'v1', credentials=creds, cache_discovery=False)
    driveService = build('drive', 'v3', credentials=creds, cache_discovery=False)

    return docService, driveService


def generateCredentials(userid):
    """Generates credentials for use by the application.
    SCOPES is a list of google api scopes to be used
    Ex) SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    """
    #creds = ServiceAccountCredentials.from_json_keyfile_name(credentialsFilepath, scopes=SCOPES)

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        groupObj = Group.objects.get(id=userid)
        credsDecoded = groupObj.token
        creds = credsDecoded.decode('base64')
    except:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            groupObj = Group.objects.get(id=userid)
            token = creds.encode('base64')


    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            token = creds.encode('base64')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    user = User.objects.create_user(username='posse',password="password", is_active=False)
    userObj = get_object_or_404(User, username='posse')
    group = Group.objects.create(displayName='posse',user=userObj, token=token)
    group.save()
    return creds