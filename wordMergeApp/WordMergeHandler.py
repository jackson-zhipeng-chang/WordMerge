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

def merge(request, userid):
    global docService, driveService

    docService, driveService = GoogleOAuthService.init(userid)

    # Google Doc Id of the template document that is being copied
    templateDocId = "1tCI3gonv6fCDhwfEPScHYwMqZr98EQ3y50HZQm19Xdo"
            
    fieldDictionary = {
        "[[name]]" : 'á(*)',
        "[[email]]" : 'zhipeng.chang@edmonton.ca' 
    }
    
    # Clone the template document and merge in the defined fields.
    copiedFileId = GoogleDriveService.copyFile(docService, driveService, templateDocId, fieldDictionary)

    GoogleDriveService.mergeFields(docService, driveService, copiedFileId, fieldDictionary)

    # Display the link on the Winchester page
    webViewLink = GoogleDriveService.convertToPDF(docService, driveService, copiedFileId)

    # Share the new document with everyone who has the link.
    emailAddress = []
    emailAddress.append('zchang@ualberta.ca')
    emailAddress.append('zhipeng.chang@edmonton.ca')
    #GoogleDriveService.shareWithUsers(docService, driveService, copiedFileId, emailAddress, sendNotificationEmail = True, emailMessage = 'test')

    return HttpResponse(webViewLink)

