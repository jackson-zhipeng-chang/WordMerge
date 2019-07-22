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
from decouple import config
import webbrowser
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]    

def init(userid):
    '''Initilization Function, takes SCOPES.
    '''
    group = get_object_or_404(Group, id=userid)
    creds = group.token
    docService = build('docs', 'v1', credentials=creds, cache_discovery=False)
    driveService = build('drive', 'v3', credentials=creds, cache_discovery=False)

    return docService, driveService

def getToken(request):
    if request.user.is_authenticated:
        creds = None
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                webbrowser.open("https://www.google.ca",  new=1, autoraise=True)
                credentials = json.loads(config("credentials"))
                flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
                creds = flow.run_local_server(port=0)

        user_email = request.user.email
        user = User.objects.get(email=user_email)
        if not Group.objects.filter(user=user).exists() :
            group = Group.objects.create(displayName=user.username,user=user, token=creds)
            group.save()
            return render(request, 'home.html', {'uuid':request.get_host()+ '/convert/' +str(group.id)})
        else:
            group = Group.objects.get(user=user)
            return render(request, 'home.html', {'uuid':request.get_host()+ '/convert/' +str(group.id)})

