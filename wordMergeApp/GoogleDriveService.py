from __future__ import print_function
import re
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import file, client, tools
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from django.shortcuts import render
from . import GoogleOAuthService
from django.http import HttpResponse, HttpResponseNotFound, Http404
from apiclient.http import MediaFileUpload
import json


def getFileTitle(docService, driveService, fileId):
    "Given a fileId get the title of the file using google Drive API."
    fileTitle = driveService.files().get(fileId=fileId).execute().get('name')
    return fileTitle

def copyFile(docService, driveService, fileId, newFileTitle = None):
    """Makes a Copy of a file in google drive. The file must be owned by or shared to the authenticated user.
    fileId is the fileId of the file you are going to copy.
    optionally define a title for the copied document.
    returns the fileId of the newly created file.
    """
    newFileName = newFileTitle
    if newFileName == None:
        newFileName = getFileTitle(fileId) + "_Copy"
    
    copiedFileBody =  {
        "name": newFileName
    }

    copiedFile = driveService.files().copy(
            fileId=fileId,
            body=copiedFileBody
            ).execute()
    return copiedFile.get('id')

def mergeFields(docService, driveService, fileId, fieldDictionary):
    """Merge fields into their place holders within a document.
    The fieldDictionary must contain at least one field for this function to do anything. 
    """
    if len(fieldDictionary) > 0:
        requests = []
        for key,val in fieldDictionary.items():
            request = {
                'replaceAllText': {
                    'containsText': {
                        'text': key,
                        'matchCase': 'true'
                    },
                    'replaceText': str(val or ''),
                }
            }
            requests.append(request)
    
        docService.documents().batchUpdate(documentId=fileId, body={'requests': requests}).execute()

def shareFile(docService, driveService, fileId, role = "reader", emailMessage=None):
    """Shares a file with everyone.    
    role is the access level being shared on the file. (owner, organizer, fileOrganizer, writer, commenter, reader)       
    """
    driveService.permissions().create(
        body=
        {
            "role": role,
            "type":"anyone"
        },
        emailMessage=emailMessage,
        fileId=fileId
        ).execute()

def convertToPDF(docService, driveService, googleDocId):
    """Downloads the given google document as a PDF file.
    Saves it as a POSSE document on the object.
    """
    fileTitle = getFileTitle(docService, driveService, googleDocId)
    fileTitle += '.pdf'
    pdfFile = driveService.files().export(fileId=googleDocId, mimeType="application/pdf").execute()
    filePath = 'tmp/'+fileTitle
    with open(filePath, "wb") as f:
        f.write(pdfFile)
    file_metadata = {'name': fileTitle}
    media = MediaFileUpload(filePath, mimetype='application/pdf')
    file = driveService.files().create(body=file_metadata,media_body=media, fields='webViewLink').execute()
    os.remove(filePath)