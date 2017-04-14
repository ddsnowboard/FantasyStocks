from json import dumps
from urllib import request, parse
from django.conf import settings
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

class AndroidToken(models.Model):
    URL = "https://fcm.googleapis.com/fcm/send"
    TOKEN = settings.FCM_TOKEN
    FIREBASE_ID_KEY_LENGTH = 200
    user = models.ForeignKey(User, null=False)
    token = models.CharField(max_length=FIREBASE_ID_KEY_LENGTH, null=False)

    @staticmethod
    def pingUser(user, title, message):
        tokens = AndroidToken.object.filter(user=user)
        for t in tokens:
            t.ping(title, message)

    def ping(self, title, message):
        SUCCESS = 200
        headers = {"Authorization": "key=" + AndroidToken.TOKEN, "Content-Type": "application/json"}
        data = dumps({"to": self.token, "notification": {"title": title, "message": message}})
        rq = request.Request(AndroidToken.URL, data=data.encode("UTF-8"), headers=headers)
        response = request.urlopen(rq)
        if not response.status == 200:
            raise RuntimeError(response.read())
