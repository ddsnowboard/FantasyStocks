from django.db import models
from django.http import HttpResponse
from urllib import request
from urllib.parse import urlencode
from django.utils import timezone
import json
from django.contrib.auth.models import User


# This gets the location for the image files for the Stock model. 
def get_upload_location(instance, filename):
    return instance.symbol


class Stock(models.Model):
    company_name = models.CharField(max_length=50, default="")
    symbol = models.CharField(max_length=4, primary_key=True)
    last_updated = models.DateTimeField()
    image = models.ImageField(upload_to=get_upload_location)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    def __str__(self):
        return "{} ({})".format(self.company_name, self.symbol)
    def update(self):
        URL = "http://dev.markitondemand.com/Api/v2/Quote/json?"
        jsonObj = json.loads(request.urlopen(URL + urlencode({"symbol" : self.symbol})).read().decode("UTF-8"))
        self.price = jsonObj['LastPrice']
        self.last_updated = timezone.now()
        self.save()

class Floor(models.Model):
    OPEN = "open"
    CLOSED = "closed"
    PERMISSIVE = "permissive"
    PERMISSIVENESS_CHOICES = (
            (OPEN, "Open"), 
            (CLOSED, "Closed"), 
            (PERMISSIVE, "Permissive")
            )
    stocks = models.ManyToManyField(Stock)
    permissiveness = models.CharField(max_length=15, choices=PERMISSIVENESS_CHOICES, default=PERMISSIVE)

# NB This model represents a specific player on a specific floor. The player account is represented by a Django `User`
# object, which this references. Setting these as ForeignKeys as opposed to something else will cause this object to be 
# deleted if the it's `User` object or its floor is deleted. 
class Player(models.Model):
    user = models.ForeignKey(User)
    floor = models.ForeignKey(Floor)

