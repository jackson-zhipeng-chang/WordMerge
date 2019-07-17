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
from django.http import HttpResponse, HttpResponseNotFound, Http404

SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]    

def init(userid):
    '''Initilization Function, takes SCOPES.
    '''
    creds = generateCredentials(userid)
    docService = build('docs', 'v1', credentials=creds, cache_discovery=False)
    driveService = build('drive', 'v3', credentials=creds, cache_discovery=False)

    return docService, driveService


def generateCredentials(userid):
    '''Generates credentials for use by the application.
    SCOPES is a list of google api scopes to be used
    Ex) SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    '''
    creds = None
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
    '''Generates credentials for use by the application.
    SCOPES is a list of google api scopes to be used
    Ex) SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    '''

    creds = None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

    user = User.objects.create_user(username=username,password='password')
    group = Group.objects.create(displayName=username,user=user, token=creds)
    group.save()

    return HttpResponse(group.id)