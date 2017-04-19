from django.db import models
from django.http import HttpResponse
from django.template import Template, Context
from urllib import request
from urllib.error import HTTPError
from urllib.parse import urlencode
from django.utils import timezone
import csv
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

def userJSON(user):
    retval = {}
    retval['id'] = user.id
    retval['username'] = user.username
    retval['players'] = [p.toShortJSON() for p in Player.objects.filter(user=user)]
    return retval

def userShortJSON(user):
    retval = {}
    retval['id'] = user.id
    retval['username'] = user.username
    retval['players'] = [p.pk for p in Player.objects.filter(user=user)]
    return retval

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
    def __repr__(self):
        return str(self)

class Stock(models.Model):
    company_name = models.CharField(max_length=50, default="", blank=True)
    symbol = models.CharField(max_length=4)
    # This 20 minute delta is there so that the update() method will actually get a new price the first time 
    # it's called.
    last_updated = models.DateTimeField(default=timezone.now() - timedelta(minutes=20))
    image = models.ImageField(upload_to=get_upload_location, blank=True, default=settings.MEDIA_URL + "default")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    change = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    last_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    def __str__(self):
        return "{} ({})".format(self.company_name, self.symbol)
    def has_current_price(self):
        return not timezone.now() - self.last_updated > timedelta(minutes=15)
    def update(self):
        if not self.has_current_price():
            price = Stock.remote_load_price(self.symbol)
            price.apply(self)
            self.last_updated = timezone.now()
            self.save()
            # The database normalizes the input to two decimal places and makes 
            # sure that the negative and positive work on the dashboard, so I 
            # reload it here. With any luck, it's fast, but who knows. 
            self.refresh_from_db()
            score = self.get_score()
            # Apply points to owners
            for i in Player.objects.filter(stocks__pk=self.pk):
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
        if self.last_price == 0:
            return 0
        return (self.price * ((self.price - self.last_price) / self.last_price)) * 100
    def format_for_json(self):
        return {"symbol": self.symbol, "name": self.company_name}

    def toJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['companyName'] = self.company_name
        retval['symbol'] = self.symbol
        retval['lastUpdated'] = self.last_updated
        retval['price'] = self.price
        retval['change'] = self.change
        retval['stockSuggestions'] = [s.toShortJSON() for s in StockSuggestion.objects.filter(stock=self)]
        return retval

    def toShortJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['companyName'] = self.company_name
        retval['symbol'] = self.symbol
        retval['lastUpdated'] = self.last_updated
        retval['price'] = self.price
        retval['change'] = self.change
        retval['stockSuggestions'] = [s.pk for s in StockSuggestion.objects.filter(stock=self)]
        return retval

    @staticmethod
    def remote_load_price(symbol):
        """
        Given a symbol as a string, returns a RemoteStockData object with the given symbol's 
        name, price, and last change. 
        """
        # This is the URL we will probably use. It returns CSV, but we'll just process it and 
        # it'll come out just like it used to. That was a good decision. Also, I might be able to 
        # do all the stocks at once now, which would be a lot faster. We'll see. 
        # Also, here's docs: http://www.jarloo.com/yahoo_finance/

        # This dict holds all the things we're getting from the API. The keys are the names, and the values
        # are the representations of those things for the API. See the docs (linked above)
        INFO = {"price": "a", "name": "n", "symbol": "s", "change": "c1", "open": "o", "close": "p"}
        URL = "http://finance.yahoo.com/d/quotes.csv?s={symbol}&f={info}"
        url = URL.format(**{"symbol": symbol, "info": "".join(INFO.values())})
        try:
            response = request.urlopen(url).read().decode("UTF-8")
        except HTTPError:
            print("Got an HTTPError")
            return Stock.remote_load_price(symbol)

        # I know dicts aren't ordered, but for an unchanging dict, dict.keys() is guaranteed to match up to dict.values()
        # Fun fact
        data = {i:j for (i, j) in zip(INFO.keys(), list(csv.reader(response.split("\n")))[0])}
        possible_prices = [data["price"], data["close"], data["open"]]
        for i in possible_prices:
            try:
                price = float(i)
            except ValueError:
                continue
            break
        else:
            raise StockAPIError("The stock {} has no price! Data is {}".format(symbol, str(data)))
        return RemoteStockData(data["symbol"], data["name"], price, data["change"])

class Floor(models.Model):
    OPEN = "open"
    CLOSED = "closed"
    PERMISSIVE = "permissive"
    PERMISSIVENESS_CHOICES = (
            (OPEN, "Open"), 
            (CLOSED, "Closed"), 
            (PERMISSIVE, "Permissive")
            )
    name = models.CharField(max_length=35, unique=True)
    stocks = models.ManyToManyField(Stock)
    permissiveness = models.CharField(max_length=15, choices=PERMISSIVENESS_CHOICES, default=PERMISSIVE)
    owner = models.ForeignKey(User, null=True)

    # By passsing the model for this as a string, we can make it be dynamically set and 
    # thus get around the fact that we haven't actually defined that class yet (it's below)
    floorPlayer = models.ForeignKey("Player", related_name="FloorPlayer", null=True)
    public = models.BooleanField(default=True)
    num_stocks = models.IntegerField(default=10)

    def save(self, *args, **kwargs):
        super(Floor, self).save(*args, **kwargs)
        if self.floorPlayer == None:
            floorUser = User.objects.get(groups__name__exact="Floor")
            newFloorPlayer = Player.objects.create(user=floorUser, floor=self)
            newFloorPlayer.save()
            self.floorPlayer = newFloorPlayer
            super(Floor, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    def leaders(self):
        return Player.objects.filter(floor=self).exclude(user__groups__name__exact="Floor").order_by("-points")
    def _render_board(self, player=None, leaderboard=False, stockboard=False, links=False):
        """
        The output of this function used to be all over the place over and over, so I consolidated it here.
        NB The output from this needs to be surrounded by `<table>` tags. 
        """
        TEMPLATE_STRING = """
                            {% load staticfiles %}
                            <tr>
                                {% if stockboard %}
                                <td style="width: 50%">
                                    <table class="stockBoard">
                                        {% for stock in stocks %}
                                        <tr>
                                                <td class="stock" id="{{ stock.symbol }}">
                                                    {% if links %}
                                                    <a class="noUnderline" href="{% url "trade" pkStock=stock.pk pkFloor=player.floor.pk %}">
                                                    {% endif %}
                                                        <span style="display: inline-block; float: left">{{ stock.symbol }}</span>
                                                    {% if links %}
                                                    </a>
                                                    {% endif %}
                                                    {% if stock.has_current_price %}
                                                    {% with change=stock.get_change %}
                                                    <span class="stockPrice {% if change > 0 %}green{% elif change == 0 %}blue{% else %}red{% endif %}">{% if change > 0 %}+{% endif %}{{ change }}</span>
                                                    {% endwith %}
                                                    {% else %}
                                                    <span class="loadingPrice stockPrice" id="{{ stock.symbol }}"><img class="loadingWheel" src="{% static "spinning-wheel.gif" %}" /></span>
                                                    {% endif %}
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
                                                        <td {% if forloop.last %}style="border-bottom: none;"{% endif %} class="playerLine" id="{{ competitor.player.pk }}" data-stocks="{{ competitor.stocks|join:"," }}">
                                                            <a class="noUnderline" href="{% url "userPage" pkUser=competitor.player.user.pk %}">
                                                            <span style="display: inline-block; float: left">{{ forloop.counter }}. {{ competitor.player.get_name }}
                                                            </span>
                                                            </a>
                                                            <span style="display: inline-block; float: right">{{ competitor.player.points }}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                    {% endfor %}
                                                </table>
                                            </td>
                                            {% endif %}
                                            </tr>
                            <script src="{% url "stockBoardJavaScript" %}"></script>
                """
        test = {p.pk : [s.symbol for s in p.stocks.all()] for p in self.leaders()}
        tem = Template(TEMPLATE_STRING)
        con = Context({"leaderboard" : leaderboard,
            "stockboard" : stockboard,
            "player": player,
            "leaders": [{"player": p, "stocks": [s.symbol for s in p.stocks.all()]} for p in self.leaders()],
            "stocks": self.stocks.all(), 
            "links": links})
        return tem.render(con)

    def render_leaderboard(self, player, links=False):
        return self._render_board(player=player, leaderboard=True, links=links)
    def render_stockboard(self, player, links=False):
        return self._render_board(player=player, stockboard=True, links=links)
    def render_both_boards(self, player, links=False):
        return self._render_board(player=player, stockboard=True, leaderboard=True, links=links)
    def to_json(self):
        return {"stocks": ",".join(s.symbol for s in self.stocks.all()),
                "name": self.name, "permissiveness": self.permissiveness, "pkOwner": self.owner.pk, 
                "pkFloorPlayer": self.floorPlayer.pk, "public": self.public, "num_stocks": self.num_stocks}

    def toJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['name'] = self.name
        retval['permissiveness'] = self.permissiveness
        retval['owner'] = userShortJSON(self.owner)
        retval['floorPlayer'] = self.floorPlayer.toShortJSON()
        retval['public'] = self.public
        retval['numStocks'] = self.num_stocks
        retval['stocks'] = [s.toShortJSON() for s in self.stocks.all()]
        return retval

    def toShortJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['name'] = self.name
        retval['permissiveness'] = self.permissiveness
        retval['owner'] = self.owner.pk
        retval['floorPlayer'] = self.floorPlayer.pk
        retval['public'] = self.public
        retval['numStocks'] = self.num_stocks
        retval['stocks'] = [s.pk for s in self.stocks.all()]
        return retval


class Player(models.Model):
    """
    This model represents a specific player on a specific floor. The player account is represented by a Django `User`
    object, which this references. Setting these as ForeignKeys as opposed to something else will cause this object to be 
    deleted if the it's `User` object or its floor is deleted. 
    """
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
        return StockSuggestion.objects.filter(floor__owner=self.user, floor=self.floor)
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
    def get_floor_leaderboard_clickable(self):
        return self.floor.render_leaderboard(self, links=True)
    def get_floor_stockboard_clickable(self):
        return self.floor.render_stockboard(self, links=True)
    def get_both_floor_boards_clickable(self):
        return self.floor.render_both_boards(self, links=True)
    def get_users_owned_floors(self):
        return Floor.objects.filter(owner=self.user)
    def to_json(self):
        return {"pkUser": self.user.pk, "pkFloor": self.floor.pk, "stocks": ",".join([s.symbol for s in self.stocks.all()]), "points": self.points}

    def toJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['user'] = userShortJSON(self.user)
        retval['floor'] = self.floor.toShortJSON()
        retval['stocks'] = [s.toShortJSON() for s in self.stocks.all()]
        retval['points'] = self.points
        retval['isFloor'] = self.isFloor()
        retval['sentTrades'] = [t.toShortJSON() for t in Trade.objects.filter(sender=self)]
        retval['receivedTrades'] = [t.toShortJSON() for t in Trade.objects.filter(recipient=self)]
        retval['isFloorOwner'] = self.floor.owner == self.user
        return retval

    def toShortJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['user'] = self.user.pk
        retval['floor'] = self.floor.pk
        retval['stocks'] = [s.pk for s in self.stocks.all()]
        retval['points'] = self.points
        retval['isFloor'] = self.isFloor()
        retval['sentTrades'] = [t.pk for t in Trade.objects.filter(sender=self)]
        retval['receivedTrades'] = [t.pk for t in Trade.objects.filter(recipient=self)]
        retval['isFloorOwner'] = self.floor.owner == self.user
        return retval

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
        if not self.recipient.isFloor():
            self.verify()
        for s in [i for i in self.recipientStocks.all() if not StockSuggestion.objects.filter(floor=self.floor, stock=i)]:
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
                    raise RuntimeError("One of the recipient stocks ({}) doesn't belong to the recipient ({})".format(s, self.recipient.user))
                if not s in self.floor.stocks.all():
                    raise RuntimeError("One of the recipient stocks ({}) doesn't belong to the floor ({})".format(s, self.floor))

        for s in self.senderStocks.all():
            if not s in self.sender.stocks.all():
                raise RuntimeError("One of the sender stocks ({}) doesn't belong to the sender ({})".format(s, self.recipient.user))
            if not s in self.floor.stocks.all():
                raise RuntimeError("One of the sender stocks ({}) doesn't belong to the floor ({})".format(s, self.floor))

        if self.recipient.stocks.all().count() + self.senderStocks.all().count() - self.recipientStocks.all().count() > self.floor.num_stocks and not self.recipient.isFloor():
            raise TradeError("{} will have too many stocks if this trade goes through".format(self.recipient.get_name()))

        if self.sender.stocks.all().count() + self.recipientStocks.all().count() - self.senderStocks.all().count() > self.floor.num_stocks:
            raise TradeError("{} will have too many stocks if this trade goes through".format(self.sender.get_name()))

        if self.recipient.isFloor():
            self.accept()
        elif self.sender.isFloor():
            raise RuntimeError("The floor sent a trade. This isn't good at all.")
    def toFormDict(self):
        d = {"other_user": self.sender.get_name(),
                "user_stocks": ",".join(i.symbol for i in self.recipientStocks.all()),
                "other_stocks": ",".join(i.symbol for i in self.senderStocks.all())}
        return d

    def toJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['recipientPlayer'] = self.recipient.toShortJSON()
        retval['recipientStocks'] = [s.toShortJSON() for s in self.recipientStocks.all()]
        retval['senderPlayer'] = self.sender.toShortJSON()
        retval['senderStocks'] = [s.toShortJSON() for s in self.senderStocks.all()]
        retval['floor'] = self.floor.toShortJSON()
        retval['date'] = self.date.isoformat()
        return retval

    def toShortJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['recipientPlayer'] = self.recipient.pk
        retval['recipientStocks'] = [s.pk for s in self.recipientStocks.all()]
        retval['senderPlayer'] = self.sender.pk
        retval['senderStocks'] = [s.pk for s in self.senderStocks.all()]
        retval['floor'] = self.floor.pk
        retval['date'] = self.date.isoformat()
        return retval

class StockSuggestion(models.Model):
    """
    This is what holds someone's request for a stock to be added to a permissive floor.
    """
    stock = models.ForeignKey(Stock)
    requesting_player = models.ForeignKey(Player)
    floor = models.ForeignKey(Floor)
    date = models.DateTimeField(auto_now_add=True)
    def accept(self):
        if not self.stock in self.floor.stocks.all():
            self.floor.stocks.add(self.stock)
            self.floor.save()
            # Adds a stock to the floor if the person who originally wanted it already has too many.
            if self.requesting_player.stocks.all().count() + 1 > self.floor.num_stocks:
                self.floor.floorPlayer.stocks.add(self.stock)
                self.floor.floorPlayer.save()
            else:
                self.requesting_player.stocks.add(self.stock)
                self.requesting_player.save()
        self.delete()
    def __str__(self):
        return "{} wants {} added to {}".format(self.requesting_player.get_name(), self.stock, self.floor)

    def toJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['stock'] = self.stock.toShortJSON()
        retval['requestingPlayer'] = self.requesting_player.toShortJSON()
        retval['floor'] = self.floor.toShortJSON()
        retval['date'] = self.date.isoformat()
        return retval

    def toShortJSON(self):
        retval = {}
        retval['id'] = self.pk
        retval['stock'] = self.stock.pk
        retval['requestingPlayer'] = self.requesting_player.pk
        retval['floor'] = self.floor.pk
        retval['date'] = self.date.isoformat()
        return retval
