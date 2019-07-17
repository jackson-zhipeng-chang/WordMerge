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
from . import GoogleOAuthService, GoogleDriveService
from django.http import HttpResponse, HttpResponseNotFound, Http404
from apiclient.http import MediaFileUpload
import json

'''
GET http://127.0.0.1:8000/convert/2ca9f276-7f7f-4f0b-bff3-a40a2008764c
Content-Type:application/json
X-DOCID:1n4sgKyxZp8qpU3KwkFclYL1fr_EskIOOEkqOI_Fh158
X-FIELDDIC:{"name":"test","email":"zhipeng.chang@edmonton.ca"}
X-SHARE:["zchang@ualberta.ca","zchang0302@gmail.com"]
'''

def merge(request, userid):
    # Google Doc Id of the template document that is being copied

    if ("HTTP_X_DOCID" in request.META) and ("HTTP_X_FIELDDIC" in request.META):
        docService, driveService = GoogleOAuthService.init(userid)
        
        shareWithUsers = False
        templateDocId = request.META["HTTP_X_DOCID"]
        fieldDictionary = json.loads(request.META["HTTP_X_FIELDDIC"])
        if "HTTP_X_SHARE" in request.META:
            shareWithUsers = True
            emailAddress = json.loads(request.META["HTTP_X_SHARE"])
    
        # Clone the template document and merge in the defined fields.
        copiedFileId = GoogleDriveService.copyFile(docService, driveService, templateDocId, fieldDictionary)

        # Merge in the defined fields.
        GoogleDriveService.mergeFields(docService, driveService, copiedFileId, fieldDictionary)

        # Display the link 
        webViewLink = GoogleDriveService.convertToPDF(docService, driveService, copiedFileId)

        # Share the new document with the list of users
        if shareWithUsers:
            GoogleDriveService.shareWithUsers(docService, driveService, copiedFileId, emailAddress, sendNotificationEmail = True, emailMessage = 'test')

        return HttpResponse(webViewLink)

    else:
        return HttpResponse("Please specify the Doc ID and Variables dictionary")
