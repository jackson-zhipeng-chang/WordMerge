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
from .models import Group, History
from django.contrib.auth import login, authenticate, logout
from threading import Thread
import queue

def merge(que, request, userid):
    # Google Doc Id of the template document that is being copied

    if ("HTTP_X_DOCID" in request.META) and ("HTTP_X_FIELDDIC" in request.META):
        if not Group.objects.filter(id=userid).exists():
            messag = 'User not found: %s'%(userid)
            response = JsonResponse({'message': messag}, status = 400)
            que.put(response)
        else:
            docService, driveService = GoogleOAuthService.init(userid)
            shareWithUsers = False
            emailMessage = None
            parents_folder = []
            newFileTitle = None
            try:
                templateDocId = request.META["HTTP_X_DOCID"]
                fieldDictionary = json.loads(request.META["HTTP_X_FIELDDIC"])
            except Exception as e:
                messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_DOCID or HTTP_X_FIELDDIC")
                response = JsonResponse({'message': messag}, status = 400)
                que.put(response)

            if "HTTP_X_SHARE" in request.META:
                try:
                    shareWithUsers = True
                    emailAddress = json.loads(request.META["HTTP_X_SHARE"])
                except Exception as e:
                    messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_SHARE")
                    response = JsonResponse({'message': messag}, status = 400)
                    que.put(response)

                    if "HTTP_X_MESSAGE" in request.META:
                        try:
                            emailMessage = json.loads(request.META["HTTP_X_MESSAGE"])
                        except Exception as e:
                            messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_MESSAGE")
                            response = JsonResponse({'message': messag}, status = 400)
                            que.put(response)

            if "HTTP_X_FOLDER" in request.META:
                try:
                    parents_folder = json.loads(request.META["HTTP_X_FOLDER"])
                except Exception as e:
                    messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_FOLDER")
                    response = JsonResponse({'message': messag}, status = 400)
                    que.put(response)  

            if "HTTP_X_NEWTITLE" in request.META:
                try:
                    newFileTitle = json.loads(request.META["HTTP_X_NEWTITLE"])
                except Exception as e:
                    messag = 'Exception: %s. Headers %s'%(e, "HTTP_X_NEWTITLE")
                    response = JsonResponse({'message': messag}, status = 400)
                    que.put(response)

            # Copy the template document and merge in the defined fields.
            try:
                copiedFileId = GoogleDriveService.copyFile(docService, driveService, templateDocId, newFileTitle)
            except Exception as e:
                messag = 'Exception: %s. When copy the file'%(e)
                response = JsonResponse({'message': messag}, status = 400)
                que.put(response)

            if copiedFileId is None:
                message = 'File not found: %s'%templateDocId
                response = JsonResponse({'message': message}, status = 404)
                que.put(response)

            # Merge in the defined fields.
            try:
                GoogleDriveService.mergeFields(docService, driveService, copiedFileId, fieldDictionary)
            except Exception as e:
                messag = 'Exception: %s. When merge the file'%(e)
                response = JsonResponse({'message': messag}, status = 400)
                que.put(response)

            # Display the link 
            try:
                webViewLink = GoogleDriveService.convertToPDF(docService, driveService, copiedFileId, parents_folder)
            except Exception as e:
                messag = 'Exception: %s. When convert to the PDF'%(e)
                response = JsonResponse({'message': messag}, status = 400)
                que.put(response)

            # Share the new document with the list of users
            if shareWithUsers:
                try:
                    GoogleDriveService.shareWithUsers(docService, driveService, copiedFileId, emailAddress, sendNotificationEmail = True, emailMessage = emailMessage)
                except Exception as e:
                    messag = 'Exception: %s. When share with users'%(e)
                    response = JsonResponse({'message': messag}, status = 400)
                    que.put(response)

            message = 'File has been converted, the link is: %s'%webViewLink
            response = JsonResponse({'message': message}, status = 200)
            que.put(response)

    else:
        message = "Please specify the Doc ID and Variables dictionary"
        response = JsonResponse({'message': message}, status = 400)
        que.put(response)

def logToDB(request, userid):
    payload = {}
    for key, val in request.META.items():
        if "HTTP_X" in key:
            payload[key] = val
    group = Group.objects.get(id=userid)
    user = group.user
    history = History.objects.create(group=group, user=user, payload=payload)
    history.save()

def main(request, userid):
    que = queue.Queue()
    merge_t = Thread(target = merge, args=(que, request, userid,))
    log_t = Thread(target = logToDB, args=(request, userid,))
    merge_t.start()
    log_t.start()
    merge_t.join()
    log_t.join()
    response = que.get()
    return response

def home(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        user_uuid = None
        exist_user = User.objects.get(email=user_email)
        if Group.objects.filter(user=exist_user).exists(): 
            group = Group.objects.get(user=exist_user)
            user_uuid = group.id
            histories = History.objects.filter(group = group)
            return render(request, 'home.html', {'uuid':request.get_host()+ '/convert/' +str(user_uuid), 'Histories': histories})
        else:
            return render(request, 'home.html')
    else:
        return render(request, 'home.html')

def logout_user(request):
    logout(request)
    return render(request, 'home.html')

