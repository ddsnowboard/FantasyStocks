from django.db import models
from django.http import HttpResponse
from django.template import Template, Context
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
        stockObj.last_price = stockObj.price
        stockObj.price = self.price
        stockObj.change = self.change
        if stockObj.company_name == "":
            stockObj.company_name = self.name
            stockObj.symbol = stockObj.symbol.upper()
    def __str__(self):
        return "{} at {}".format(self.symbol, self.price)

class Stock(models.Model):
    company_name = models.CharField(max_length=50, default="", blank=True)
    symbol = models.CharField(max_length=4)
    last_updated = models.DateTimeField(default=timezone.now() - timedelta(minutes=20))
    image = models.ImageField(upload_to=get_upload_location, blank=True, default=settings.MEDIA_URL + "default")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    change = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    last_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    def __str__(self):
        return "{} ({})".format(self.company_name, self.symbol)
    def update(self):
        if timezone.now() - self.last_updated > timedelta(minutes=15):
            Stock.remote_load_price(self.symbol).apply(self)
            self.last_updated = timezone.now()
            self.save()
            # The database normalizes the input to two decimal places and makes 
            # sure that the negative and positive work on the dashboard, so I 
            # reload it here. With any luck, it's fast, but who knows. 
            self.refresh_from_db()
            score = self.get_score()
            # Apply points to owners
            for i in [p for p in Player.objects.all() if self in p.stocks.all()]:
                i.points += score
                i.save()
    def force_update(self):
        self.last_updated -= timedelta(minutes=30)
        self.update()
    def get_price(self):
        self.update()
        return self.price
    def get_change(self):
        self.update()
        return self.change
    def get_score(self):
        # This is really a dummy method. I just need something so that I can make it technically work, 
        # then I'll be able to fine tune it. 
        if self.last_price == 0:
            return 0
        return (self.price * ((self.price - self.last_price) / self.last_price)) * 100
    def format_for_json(self):
        return {"symbol": self.symbol, "name": self.company_name}
    @staticmethod
    def remote_load_price(symbol):
        """
        Given a symbol as a string, returns a RemoteStockData object with the given symbol's 
        name, price, and last change. 
        """
        URL = "http://finance.yahoo.com/webservice/v1/symbols/{}/quote?format=json&view=detail"
        try:
            jsonObj = json.loads(request.urlopen(URL.format(symbol)).read().decode("UTF-8"))['list']['resources'][0]['resource']['fields']
        except IndexError:
            raise RuntimeError("The stock with symbol {} can't be found!".format(symbol))
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
    public = models.BooleanField(default=True)
    num_stocks = models.IntegerField(default=10)
    def __str__(self):
        return self.name
    def leaders(self):
        return Player.objects.filter(floor=self).exclude(user__groups__name__exact="Floor").order_by("-points")
    def _render_board(self, player=None, leaderboard=False, stockboard=False):
        """
        The output from this needs to be surrounded by `<table>` tags. 
        """
        TEMPLATE_STRING = """
                            <tr>
                                {% if stockboard %}
                                <td style="width: 50%">
                                    <table class="stockBoard">
                                        {% for stock in stocks %}
                                        <tr>
                                            {% if stock in player.stocks.all %}
                                            <td class="userStock">
                                                {% else %}
                                                <td>
                                                    {% endif %}
                                                    <a class="noUnderline" href="{% url "trade" pkStock=stock.pk pkFloor=player.floor.pk %}">
                                                        <span style="display: inline-block; float: left">{{ stock.symbol }}</span>
                                                    </a>
                                                    {% with change=stock.get_change %}
                                                    <span class="{% if change > 0 %}green{% elif change == 0 %}blue{% else %}red{% endif %}" style="display: inline-block; float: right">{% if change > 0 %}+{% endif %}{{ change }}</span>
                                                    {% endwith %}
                                                </td>
                                        </tr>
                                        {% endfor %}
                            </tr>
                                    </table>
                                            </td>
                                            {% endif %}
                                            {% if leaderboard %}
                                            <td>
                                                <table class="leaderBoard">
                                                    {% for competitor in leaders %}
                                                    <tr>
                                                        <td {% if forloop.last %}style="border-bottom: none;"{% endif %}>
                                                            <a class="noUnderline" href="{% url "userPage" pkUser=competitor.user.pk %}"<span style="display: inline-block; float: left">{{ forloop.counter }}. {{ competitor.get_name }}</span></a>
                                                            <span style="display: inline-block; float: right">{{ competitor.points }}</span>
                                                        </td>
                                                    </tr>
                                                    {% endfor %}
                                                </table>
                                            </td>
                                            {% endif %}
                                            </tr>
                                            
                """
        tem = Template(TEMPLATE_STRING)
        con = Context({"leaderboard" : leaderboard, "stockboard" : stockboard, "player": player, "leaders": self.leaders(), "stocks": self.stocks.all()})
        return tem.render(con)

    def render_leaderboard(self, player):
        return self._render_board(player=player, leaderboard=True)
    def render_stockboard(self, player):
        return self._render_board(player=player, stockboard=True)
    def render_both_boards(self, player):
        return self._render_board(player=player, stockboard=True, leaderboard=True)
    def to_json(self):
        return json.dumps({"stocks": ",".join(s.symbol for s in self.stocks.all()),
            "name": self.name, "permissiveness": self.permissiveness, "pkOwner": self.owner.pk, 
            "pkFloorPlayer": self.floorPlayer.pk, "public": self.public, "num_stocks": self.num_stocks})

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
    def isFloor(self):
        return "Floor" in [i.name for i in self.user.groups.all()]
    def receivedTrades(self):
        return Trade.objects.filter(recipient=self)
    def sentTrades(self):
        return Trade.objects.filter(sender=self)
    def receivedRequests(self):
        return StockSuggestion.objects.filter(floor__owner=self.user)
    def numMessages(self):
        num = self.receivedTrades().count()
        if self.floor.owner == self.user and self.floor.permissiveness == 'permissive':
            num += self.receivedRequests().count()
        return num
    def seesSuggestions(self):
        """
        This returns a boolean telling whether this player needs a suggestions tab on his 
        dashboard tab. 
        """
        return self.floor.owner == self.user and self.floor.permissiveness == "permissive"
    def get_floor_leaderboard(self):
        return self.floor.render_leaderboard(self)
    def get_floor_stockboard(self):
        return self.floor.render_stockboard(self)
    def get_both_floor_boards(self):
        return self.floor.render_both_boards(self)
    def get_users_owned_floors(self):
        return Floor.objects.filter(owner=self.user)
    def to_json(self):
        return json.dumps({"pkUser": self.user.pk, "pkFloor": self.floor.pk, "stocks": ",".join([s.symbol for s in self.stocks.all()]), "points": self.points})

class Trade(models.Model):
    recipient = models.ForeignKey(Player)
    # recipientStocks and senderStocks are the stocks that those people have right now and will give away in the trade. 
    recipientStocks = models.ManyToManyField(Stock, related_name="receivingPlayerStocks")
    floor = models.ForeignKey(Floor)
    sender = models.ForeignKey(Player, related_name="sendingPlayer")
    senderStocks = models.ManyToManyField(Stock)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return "Trade from {} to {} on {}".format(self.sender.user, self.recipient.user, self.floor)
    def accept(self):
        for s in self.recipientStocks.all():
            self.recipient.stocks.remove(s)
            self.sender.stocks.add(s)
        for s in self.senderStocks.all():
            self.sender.stocks.remove(s)
            self.recipient.stocks.add(s)
        self.sender.save()
        self.recipient.save()
        self.delete()
    def verify(self):
        if not (self.recipient.isFloor() and not self.floor.permissiveness == "closed"):
            for s in self.recipientStocks.all():
                if not s in self.recipient.stocks.all():
                    raise TradeError("One of the recipient stocks ({}) doesn't belong to the recipient ({})".format(s, self.recipient.user))
                if not s in self.floor.stocks.all():
                    raise TradeError("One of the recipient stocks ({}) doesn't belong to the floor ({})".format(s, self.floor))
        for s in self.senderStocks.all():
            if not s in self.sender.stocks.all():
                raise TradeError("One of the sender stocks ({}) doesn't belong to the sender ({})".format(s, self.recipient.user))
            if not s in self.floor.stocks.all():
                raise TradeError("One of the sender stocks ({}) doesn't belong to the floor ({})".format(s, self.floor))
        if self.recipient.isFloor():
            self.accept()
        elif self.sender.isFloor():
            raise RuntimeError("The floor sent a trade. This isn't good at all.")
    def toFormDict(self):
        d = {"other_user": self.sender.get_name(),
            "user_stocks": ",".join(i.symbol for i in self.recipientStocks.all()),
            "other_stocks": ",".join(i.symbol for i in self.senderStocks.all())}
        return d

class StockSuggestion(models.Model):
    stock = models.ForeignKey(Stock)
    requesting_player = models.ForeignKey(Player)
    floor = models.ForeignKey(Floor)
    date = models.DateTimeField(auto_now_add=True)
    def accept(self):
        if not self.stock in self.floor.stocks.all():
            self.floor.stocks.add(self.stock)
            self.floor.save()
            self.requesting_player.stocks.add(self.stock)
            self.requesting_player.save()
        self.delete()

