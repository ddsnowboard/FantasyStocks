from django.db import models
from urllib import request
from urllib.parse import urlencode
from django.utils import timezone
import json


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
