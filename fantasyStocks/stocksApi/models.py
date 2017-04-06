from django.db import models
from random import choice 
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User

SESSION_ID_LENGTH = 64

def generateRandomId():
    CHARACTERS = "abcdefghijlkmnopqrstuvwxyzABCDEFGHIJLKMNOPQRSTUVWXYZ1234567890"
    out = []
    for i in range(SESSION_ID_LENGTH):
        out.append(choice(CHARACTERS))
    return "".join(out)

def getExpirationDate():
    return datetime.now(timezone.utc) + timedelta(minutes=20)

class SessionId(models.Model):
    id_string = models.CharField(max_length=SESSION_ID_LENGTH, unique=True, default=generateRandomId, null=False)
    exp_date = models.DateTimeField(default=getExpirationDate, null=False)
    associated_user = models.ForeignKey(User)
    
    def is_expired(self):
        return datetime.now(timezone.utc) > self.exp_date
