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
import json
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]    

def init(userid):
    """Initilization Function, takes SCOPES.
    """
    creds = generateCredentials(userid)
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

    group = Group.objects.get(id=userid)
    creds = group.token
    '''
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
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
    '''
    return creds


def getToken(request, username):
    """Generates credentials for use by the application.
    SCOPES is a list of google api scopes to be used
    Ex) SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    """
    #creds = ServiceAccountCredentials.from_json_keyfile_name(credentialsFilepath, scopes=SCOPES)
 
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

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
    user = User.objects.create_user(username=username,password='password', is_active=True)
    group = Group.objects.create(displayName=username,user=user, token=creds)
    group.save()

    return creds