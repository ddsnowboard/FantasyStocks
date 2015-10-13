from django.db import models
from django.http import HttpResponse
from urllib import request
from urllib.parse import urlencode
from django.utils import timezone
import json
from django.contrib.auth.models import User
from datetime import timedelta


# This gets the location for the image files for the Stock model. 
def get_upload_location(instance, filename):
    return instance.symbol


class Stock(models.Model):
    company_name = models.CharField(max_length=50, default="", blank=True)
    symbol = models.CharField(max_length=4, primary_key=True)
    last_updated = models.DateTimeField(default=timezone.now() - timedelta(minutes=20))
    # Set up a default image and maybe a way to get them automatically. 
    image = models.ImageField(upload_to=get_upload_location, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    change = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    def __str__(self):
        return "{} ({})".format(self.company_name, self.symbol)
    def update(self):
        if timezone.now() - self.last_updated > timedelta(minutes=15):
            URL = "http://dev.markitondemand.com/Api/v2/Quote/json?"
            jsonObj = json.loads(request.urlopen(URL + urlencode({"symbol" : self.symbol})).read().decode("UTF-8"))
            self.price = jsonObj['LastPrice']
            self.change = jsonObj["Change"]
            self.last_updated = timezone.now()
            if self.company_name == "":
                self.company_name = jsonObj["Name"]
                self.symbol = self.symbol.upper()
            self.save()
    def get_price(self):
        self.update()
        return self.price
    def get_change(self):
        self.update()
        return self.change

class Floor(models.Model):
    OPEN = "open"
    CLOSED = "closed"
    PERMISSIVE = "permissive"
    PERMISSIVENESS_CHOICES = (
            (OPEN, "Open"), 
            (CLOSED, "Closed"), 
            (PERMISSIVE, "Permissive")
            )
    name = models.CharField(max_length=15)
    stocks = models.ManyToManyField(Stock)
    permissiveness = models.CharField(max_length=15, choices=PERMISSIVENESS_CHOICES, default=PERMISSIVE)
    def __str__(self):
        return self.name

# NB This model represents a specific player on a specific floor. The player account is represented by a Django `User`
# object, which this references. Setting these as ForeignKeys as opposed to something else will cause this object to be 
# deleted if the it's `User` object or its floor is deleted. 
class Player(models.Model):
    user = models.ForeignKey(User)
    floor = models.ForeignKey(Floor)
    def __str__(self):
        return "{} on {}".format(str(self.user), str(self.floor))
