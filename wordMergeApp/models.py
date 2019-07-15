from django.db import models
import uuid
from django.contrib.auth.models import User

'''
python3 manage.py makemigrations
python3 manage.py migrate
'''
class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    displayName = models.CharField(max_length=128)
    token = models.CharField(max_length=999, editable=False)

    def __str__(self):
        return self.displayName