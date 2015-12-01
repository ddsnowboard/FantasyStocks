from django.db import models
from django.http import HttpResponse
from urllib import request
from urllib.parse import urlencode
from django.utils import timezone
import json
from django.contrib.auth.models import User, Group
from datetime import timedelta
from django.conf import settings
import sys

# This gets the location for the image files for the Stock model. 
def get_upload_location(instance, filename):
    return instance.symbol

class StockAPIError(Exception):
    pass

class TradeError(Exception):
    pass

class RemoteStockData:
    """
    An object that holds the data received when a stock is updated
    from the web API. 
    @field symbol The symbol of the stock
    @field price The newest price available of the stock
    @field change The last available change of the stock
    @field name The name of the company
    """
    def __init__(self, symbol, name, price, change):
        self.symbol = symbol
        self.name = name
        self.price = price
        self.change = change
    def apply(self, stockObj = None):
        if not stockObj:
            stockObj = Stock.objects.get(symbol=self.symbol)
        stockObj.price = self.price
        stockObj.change = self.change
        if stockObj.company_name == "":
            stockObj.company_name = self.name
            stockObj.symbol = stockObj.symbol.upper()

class Stock(models.Model):
    company_name = models.CharField(max_length=50, default="", blank=True)
    symbol = models.CharField(max_length=4)
    last_updated = models.DateTimeField(default=timezone.now() - timedelta(minutes=20))
    # Set up a default image and maybe a way to get them automatically. 
    image = models.ImageField(upload_to=get_upload_location, blank=True, default=settings.MEDIA_URL + "default")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    change = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    def __str__(self):
        return "{} ({})".format(self.company_name, self.symbol)
    def update(self):
        if timezone.now() - self.last_updated > timedelta(minutes=15):
            p = lambda x: print(x, file=sys.stderr)
            p("Starting price load")
            Stock.remote_load_price(self.symbol).apply(self)
            p("Finished price load")
            self.last_updated = timezone.now()
            self.save()
            # The database normalizes the input to two decimal places and makes 
            # sure that the negative and positive work on the dashboard, so I 
            # reload it here. With any luck, it's fast, but who knows. 
            p("about to refresh db")
            self.refresh_from_db()
            p("refreshed db")
    def force_update(self):
        self.last_updated -= timedelta(minutes=30)
        self.update()
    def get_price(self):
        self.update()
        return self.price
    def get_change(self):
        self.update()
        return self.change
    def format_for_json(self):
        return {"symbol": self.symbol, "name": self.company_name}
    @staticmethod
    def remote_load_price(symbol):
        """
        Given a symbol as a string, returns a RemoteStockData object with the given symbol's 
        name, price, and last change. 
        """
        URL = "http://finance.yahoo.com/webservice/v1/symbols/{}/quote?format=json&view=detail"
        jsonObj = json.loads(request.urlopen(URL.format(symbol)).read().decode("UTF-8"))['list']['resources'][0]['resource']['fields']
        return RemoteStockData(jsonObj["symbol"], jsonObj["name"], jsonObj["price"], jsonObj["change"])

class Floor(models.Model):
    OPEN = "open"
    CLOSED = "closed"
    PERMISSIVE = "permissive"
    PERMISSIVENESS_CHOICES = (
            (OPEN, "Open"), 
            (CLOSED, "Closed"), 
            (PERMISSIVE, "Permissive")
            )
    name = models.CharField(max_length=35)
    stocks = models.ManyToManyField(Stock)
    permissiveness = models.CharField(max_length=15, choices=PERMISSIVENESS_CHOICES, default=PERMISSIVE)
    owner = models.ForeignKey(User, null=True)
    # The model for this ForeignKey is a string because it doesn't know what it is yet because it's down there. 
    floorPlayer = models.ForeignKey("Player", related_name="FloorPlayer", null=True)
    def __str__(self):
        return self.name
    def leaders(self):
        return Player.objects.filter(floor=self).exclude(user__groups__name__exact="Floor").order_by("-points")

# NB This model represents a specific player on a specific floor. The player account is represented by a Django `User`
# object, which this references. Setting these as ForeignKeys as opposed to something else will cause this object to be 
# deleted if the it's `User` object or its floor is deleted. 
class Player(models.Model):
    user = models.ForeignKey(User)
    floor = models.ForeignKey("Floor")
    stocks = models.ManyToManyField(Stock, blank=True)
    points = models.IntegerField(default=0)
    def __str__(self):
        return "{} on {}".format(str(self.user), str(self.floor))
    def get_name(self):
        """
        It's possible that somebody could not have a username, perhaps, so I have this to take
        care of that, and also prevent a bunch of ugly `player.user.username` calls. 
        """
        return self.user.username if self.user.username else self.user.email

class Trade(models.Model):
    recipient = models.ForeignKey(Player)
    # recipientStocks and senderStocks are the stocks that those people have right now and will give away in the trade. 
    recipientStocks = models.ManyToManyField(Stock, related_name="receivingPlayerStocks")
    floor = models.ForeignKey(Floor)
    sender = models.ForeignKey(Player, related_name="sendingPlayer")
    senderStocks = models.ManyToManyField(Stock)
    def __str__(self):
        return "Trade from {} to {} on {}".format(self.sender.user, self.recipient.user, self.floor)
    def accept(self):
        for s in self.recipientStocks.all():
            self.recipient.stocks.remove(s)
            self.sender.stocks.add(s)
        for s in self.senderStocks.all():
            self.sender.stocks.remove(s)
            self.sender.stocks.add(s)
        self.sender.save()
        self.recipient.save()
        self.delete()
    def verify(self):
        for s in recipientStocks.all():
            if not s in recipient.stocks.all():
                raise TradeError("One of the recipient stocks ({}) doesn't belong to the recipient ({})".format(s, self.recipient.user))
            if not s in floor.stocks.all():
                raise TradeError("One of the recipient stocks ({}) doesn't belong to the floor ({})".format(s, self.floor))
        for s in senderStocks.all():
            if not s in sender.stocks.all():
                raise TradeError("One of the sender stocks ({}) doesn't belong to the sender ({})".format(s, self.recipient.user))
            if not s in floor.stocks.all():
                raise TradeError("One of the sender stocks ({}) doesn't belong to the floor ({})".format(s, self.floor))
        if recipient.user.groups == "Floor":
            self.accept()
        elif sender.user.groups == "Floor":
            raise RuntimeError("The floor sent a trade. This isn't good at all.")
