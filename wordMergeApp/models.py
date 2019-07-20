from django.db import models
import uuid
from django.contrib.auth.models import User
from .oauth2client.contrib.django_util.models import CredentialsField

'''
python3 manage.py makemigrations
python3 manage.py migrate
'''
class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    displayName = models.CharField(max_length=128)
    token = CredentialsField(        
        editable=False,
        blank=True,
        null=True,)

    def __str__(self):
        return self.displayName


class History(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    payload = models.TextField(null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user.email