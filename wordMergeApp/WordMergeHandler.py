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
from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from apiclient.http import MediaFileUpload
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Group
from django.contrib.auth import login, authenticate, logout



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
        emailMessage = None
        parents_folder = []
        try:
            templateDocId = request.META["HTTP_X_DOCID"]
            fieldDictionary = json.loads(request.META["HTTP_X_FIELDDIC"])
        except Exception as e:
            messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_DOCID or HTTP_X_FIELDDIC")
            response = JsonResponse({'message': messag}, status = 400)
            return response

        if "HTTP_X_SHARE" in request.META:
            try:
                shareWithUsers = True
                emailAddress = json.loads(request.META["HTTP_X_SHARE"])
            except Exception as e:
                messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_SHARE")
                response = JsonResponse({'message': messag}, status = 400)
                return response

                if "HTTP_X_MESSAGE" in request.META:
                    try:
                        emailMessage = json.loads(request.META["HTTP_X_MESSAGE"])
                    except Exception as e:
                        messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_MESSAGE")
                        response = JsonResponse({'message': messag}, status = 400)
                        return response

        if "HTTP_X_FOLDER" in request.META:
            try:
                parents_folder = json.loads(request.META["HTTP_X_FOLDER"])
            except Exception as e:
                messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_FOLDER")
                response = JsonResponse({'message': messag}, status = 400)
                return response   

        # Clone the template document and merge in the defined fields.
        try:
            copiedFileId = GoogleDriveService.copyFile(docService, driveService, templateDocId, fieldDictionary)
        except Exception as e:
            messag = 'Exception: %s. When copy the file'%(e)
            response = JsonResponse({'message': messag}, status = 400)
            return response 

        if copiedFileId is None:
            message = 'File not found: %s'%templateDocId
            response = JsonResponse({'message': message}, status = 404)
            return response

        # Merge in the defined fields.
        try:
            GoogleDriveService.mergeFields(docService, driveService, copiedFileId, fieldDictionary)
        except Exception as e:
            messag = 'Exception: %s. When merge the file'%(e)
            response = JsonResponse({'message': messag}, status = 400)
            return response 

        # Display the link 
        try:
            webViewLink = GoogleDriveService.convertToPDF(docService, driveService, copiedFileId, parents_folder)
        except Exception as e:
            messag = 'Exception: %s. When convert to the PDF'%(e)
            response = JsonResponse({'message': messag}, status = 400)
            return response 

        # Share the new document with the list of users
        if shareWithUsers:
            try:
                GoogleDriveService.shareWithUsers(docService, driveService, copiedFileId, emailAddress, sendNotificationEmail = True, emailMessage = emailMessage)
            except Exception as e:
                messag = 'Exception: %s. When share with users'%(e)
                response = JsonResponse({'message': messag}, status = 400)
                return response 

        message = 'File has been converted, the link is: %s'%webViewLink
        response = JsonResponse({'message': message}, status = 200)
        return response

    else:
        message = "Please specify the Doc ID and Variables dictionary"
        response = JsonResponse({'message': message}, status = 400)
        return response

def home(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        user_uuid = None
        exist_user = User.objects.get(email=user_email)
        if Group.objects.filter(user=exist_user).exists(): 
            group = Group.objects.get(user=exist_user)
            user_uuid = group.id
        return render(request, 'home.html', {'uuid':request.get_host()+ '/convert/' +str(user_uuid)})
    else:
        return render(request, 'home.html')

def logout_user(request):
    logout(request)
    return render(request, 'home.html')

