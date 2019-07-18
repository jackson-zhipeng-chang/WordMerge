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

SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/gmail.metadata"]    

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
    group = get_object_or_404(Group, id=userid)
    creds = group.token
    return creds


def getToken(request):
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
    user_email = get_user_info(creds)

    if not User.objects.filter(username=user_email).exists() :
        user = User.objects.create_user(username=user_email,email=user_email, password='password', is_active=False)
        group = Group.objects.create(displayName=user_email,user=user, token=creds)
        group.save()
        return HttpResponse(group.id)
    else:
        exist_user = User.objects.get(username=user_email,email=user_email)
        if not Group.objects.filter(user=exist_user).exists() :
            group = Group.objects.create(displayName=user_email,user=user, token=creds)
            group.save()
            message = 'You already have an account: %s'%group.id
            return HttpResponse(message)
        else:
            group = Group.objects.get(user=exist_user)
            message = 'You already have an account: %s'%group.id
            return HttpResponse(message)

def get_user_info(creds):
    gmailService = build('gmail', 'v1', credentials=creds)
    user_info = gmailService.users().getProfile(userId='me').execute()
    return user_info['emailAddress']
