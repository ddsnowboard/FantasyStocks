from random import randint
from django.conf.urls.static import static
from functools import reduce
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy, reverse
from stocks.models import Floor, Stock, StockAPIError, StockSuggestion
from django.core.exceptions import ValidationError
from stocks.models import Floor, Player, Trade
import sys

class StockWidget(forms.widgets.TextInput):
    """
    This widget allows the user to select any stock, whether or not 
    it's in the database. It gets the list of stocks from the big JSON
    list "stocks.json" in the static folder. This *must* be used with a StockChoiceField
    unless you've done the sufficient work somewhere else. 
    """
    HTML_CLASS = "stockBox"
    def __init__(self, prefetchPlayerPk=None, attrs=None):
        newAttrs = attrs.copy() if attrs else {}
        newAttrs['class'] = self.HTML_CLASS
        super(StockWidget, self).__init__(newAttrs)
        # If there is no attrs object, we can assume we need every stock and keep things simple
        if self.attrs.get('id', None):
            self.attrs = attrs
            self.attrs["class"] = StockWidget.HTML_CLASS
            self.prefetchPlayerPk = prefetchPlayerPk
        else:
            self.attrs["id"] = "StockWidgetId"
            self.prefetchPlayerPk = None
    def _media(self):
        js = ["//code.jquery.com/jquery-1.11.3.min.js",
        "typeahead.bundle.js", "common.js",]
        # See above comment
        if not self.prefetchPlayerPk:
            js.append(reverse("stockWidgetJavascript", kwargs={"identifier" : self.attrs['id']}))
        else:
            js.append(reverse("stockWidgetJavascript", kwargs={"identifier" : self.attrs['id'], "player" : self.prefetchPlayerPk}))
        return forms.Media(js=js)
    media = property(_media)
    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = {}
        attrs['id'] = self.attrs['id']
        return super(StockWidget, self).render(name, value, attrs)

class UserChoiceWidget(forms.widgets.TextInput):
    WIDGET_ID = "playerChoiceWidget"
    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}
        attrs["id"] = self.WIDGET_ID
        super().__init__(attrs)
    def _media(self):
        js = ["//code.jquery.com/jquery-1.11.3.min.js",  "typeahead.bundle.js", "common.js", reverse_lazy("playerFieldJS", kwargs={"identifier" : self.WIDGET_ID}),]
        return forms.Media(js=js)
    media = property(_media)

class StockChoiceField(forms.Field):
    widget = StockWidget
    def __init__(self, *args, **kwargs):
        super(StockChoiceField, self).__init__(*args, **kwargs)
    def to_python(self, value):
        out = []
        if not value:
            return out
        symbols = value.split(",")
        if not len(set(symbols)) == len(symbols):
            raise ValidationError("There was a duplicate stock!")
        for i in symbols:
            s = Stock.objects.filter(symbol=i)
            if s:
                s = s[0]
            else:
                s = Stock(symbol=i)
                try:
                    s.update()
                except StockAPIError:
                    raise ValidationError
                s.save()
            out.append(s)
        return out

class UserField(forms.Field):
    """
    This returns a `User` object, not just a string. 
    """
    widget = UserChoiceWidget
    def __init__(self, floor=None, other=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def to_python(self, value):
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist:
            raise ValidationError("That was an invalid user")
        except MultipleObjectsReturned:
            raise ValidationError("There is more than one user with that name") 

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=25)
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput)
    nextPage = forms.CharField(label="next page", max_length=30, widget=forms.HiddenInput(), initial=reverse_lazy("dashboard"))

class RegistrationForm(forms.Form):
    # The order of this constant matters. Tripping `already_exists` doesn't make 
    # any sense if `dontmatch` has already been tripped. 
    POSSIBLE_ERRORS = ("dontmatch", "already_exists")
    username = forms.CharField(label="Username", max_length=25)
    email = forms.EmailField(label="Email", max_length=100)
    password1 = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm", max_length=50, widget=forms.PasswordInput)
    nextPage = forms.CharField(label="next page", max_length=30, widget=forms.HiddenInput(), initial=reverse_lazy("dashboard"))
    def is_valid(self):
        if not super(RegistrationForm, self).is_valid():
            return False
        if User.objects.filter(email=self.cleaned_data["email"]).exists() or User.objects.filter(username=self.cleaned_data["username"]):
            self._errors["already_exists"] = "That email or username is already taken"
            return False
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            self._errors["dontmatch"] = "Your passwords don't match"
            return False
        return True
    def get_errors(self):
        if not self.is_valid():
            for i in self.POSSIBLE_ERRORS:
                if i in self._errors:
                    return self._errors[i]
            return "There was an error with your registration"
        return ""

class FloorForm(forms.Form):
    name = forms.CharField(label="Name", max_length=35)
    privacy = forms.BooleanField(label="Private?:", help_text="<em>If the floor is private, it won't show up on the join floor page,<br /> and you'll have to send a link to allow people to join it.</em>", required=False) 
    number_of_stocks = forms.IntegerField(label="Maximum Number of Stocks (per player)", min_value=1, max_value=1000)
    stocks = StockChoiceField(label="Stocks")
    permissiveness = forms.ChoiceField(label="Permissiveness", choices=Floor.PERMISSIVENESS_CHOICES)
    def __init__(self, *args, user=None, floor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and floor:
            stocks = StockChoiceField(label="Stocks")
        elif not user and not floor:
            pass
        else:
            raise RuntimeError("You have to either pass in a user and a floor, or neither.")
    def is_valid(self):
        return super(FloorForm, self).is_valid()
    def save(self):
        floor = Floor(name=self.cleaned_data['name'],
                permissiveness=self.cleaned_data['permissiveness'],
                num_stocks=self.cleaned_data["number_of_stocks"],
                public=not self.cleaned_data["privacy"])
        floor.save()
        for i in self.cleaned_data['stocks']:
            floor.stocks.add(i)
        floor.save()
        return floor


class TradeForm(forms.Form):
    other_user = UserField(label="Other Player")
    user_stocks = StockChoiceField(label="Your Stocks", required=False)
    other_stocks = StockChoiceField(label="Other player's stocks", required=False)
    def is_valid(self, pkFloor=None, user=None, pkCountering=None):
        """
        You have to give this function the floor number or else it won't know where 
        to look. You also need to give it the user object so it can find its player.
        """
        if not super().is_valid():
            return False
        error = False
        if not pkFloor:
            raise RuntimeError("""You need to give a floor to 
                TradeForm.is_valid() or else it won't know what to look for.""")
        elif not user:
            raise RuntimeError("""You need to give the user object to 
                TradeForm.is_valid() or else it won't know what to look for.""")
        try:
            floor = Floor.objects.get(pk=pkFloor)
        except Floor.DoesNotExist:
            raise RuntimeError("""The floor with primary key {} doesn't exist""".format(floor))
        other = self.fields["other_user"].to_python(self.data["other_user"])
        try:
            other_player = Player.objects.get(floor=floor,
                    user=other)
        except Player.DoesNotExist:
            self.add_error("other_player", ValidationError("""The other player does not exist""", code="invalidother"))
            error = True
        try:
            user_player = Player.objects.get(floor=floor, user=user)
        except Player.DoesNotExist:
            self.add_error(None, ValidationError("""The user player does not exist""", code="invaliduser"))
            error = True
        user_stocks = self.fields["user_stocks"].to_python(self.data["user_stocks"])
        for s in user_stocks:
            if not s in user_player.stocks.all():
                self.add_error("user_stocks", ValidationError("""The stock {} does not belong to the user
                {} on floor {}""".format(s.symbol, user_player.user.username,
                    floor.name, code="invaliduserstock")))
                error = True
        other_stocks = self.fields["other_stocks"].to_python(self.data["other_stocks"])
        for s in other_stocks:
            if not s in other_player.stocks.all()[:]:
                if other_player.isFloor() and floor.permissiveness == "permissive":
                    suggestion = StockSuggestion(stock=s, requesting_player=user_player, floor=floor)
                    suggestion.save()
                elif other_player.isFloor() and floor.permissiveness == "open":
                    floor.stocks.add(s)
                else:
                    self.add_error("other_user", ValidationError("""The stock {} does not belong to the user
                {} on floor {}""".format(s.symbol, other_player.user.username,
                    floor.name), code="invalidotherstock"))
                    error = True
        stocks_in_trades = []
        trades = Trade.objects.filter(floor=floor)
        if pkCountering:
            trades = trades.exclude(pk=pkCountering)
        for i in trades:
            if i.senderStocks: 
                stocks_in_trades.extend(i.senderStocks.all())
            if i.recipientStocks: 
                stocks_in_trades.extend(i.recipientStocks.all())
        for i in user_stocks:
            if i in stocks_in_trades:
                self.add_error("user_stocks", ValidationError("The stock %(stock)s is already being traded by you",
                    params={"stock": i}))
                error = True
        for i in other_stocks:
            if i in stocks_in_trades:
                self.add_error("other_stocks", ValidationError("The stock %(stock)s is already being traded by %(other)s",
                    params={"stock": i, "other": other_player.user}))
                error = True
        if not other_stocks and not user_stocks:
            self.add_error(None, ValidationError("""The trade is empty!""", code="empty"))
            error = True
        max_stocks = floor.num_stocks
        if user_player.stocks.all().count() - len(user_stocks) + len(other_stocks) > max_stocks:
            self.add_error(None, ValidationError("If this trade is accepted, you will have too many stocks."))
            error = True
        elif not other_player.isFloor() and other_player.stocks.all().count() - len(other_stocks) + len(user_stocks) > max_stocks:
            self.add_error(None, ValidationError("If this trade is accepted, %(other)s will have too many stocks.", params={"other": other_player.get_name()}))
            error = True
        return not error
    def to_trade(self, floor=None, user=None):
        floor = Floor.objects.get(pk=floor)
        trade = Trade.objects.create(floor=floor,
                sender=Player.objects.get(floor=floor, user=user),
                recipient=Player.objects.get(user=self.cleaned_data["other_user"], floor=floor))
        for i in self.cleaned_data.get("other_stocks", []):
            trade.recipientStocks.add(i)
        for i in self.cleaned_data.get("user_stocks", []):
            trade.senderStocks.add(i)
        trade.save()
        trade.verify()
        return trade
    def get_widget_media(self):
        otherMedia = forms.Media()
        for i in self.fields.values():
            otherMedia += i.widget.media
        return otherMedia
    def _media(self):
        # There is usually such good design in django. 
        # I don't know where it went here. O well. 
        # At least I know that the scripts will be in the order I want. 
        js = (reverse("tradeCommonJavaScript"), reverse("tradeFormJavaScript"), )
        return self.get_widget_media() + forms.Media(js=js)
    media = property(_media)

class ReceivedTradeForm(TradeForm):
    def _media(self):
        js = (reverse("tradeCommonJavaScript"), reverse("receivedTradeJavascript"), )
        return self.get_widget_media() + forms.Media(js=js)
    media = property(_media)

class UserEditingForm(forms.Form):
    """
    This will be the form that will take care of letting the user
    edit his or her account. I would use a ModelForm, but I want more 
    control, so I'll do this.
    """
    username = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField()
    primary_key = forms.IntegerField(widget=forms.HiddenInput, required=True)
    def save(self):
        if self.is_valid():
            try:
                user = User.objects.get(pk=self.cleaned_data["primary_key"])
                user.first_name = self.cleaned_data["first_name"]
                user.last_name = self.cleaned_data["last_name"]
                user.email = self.cleaned_data["email"]
                user.save()
            except User.DoesNotExist:
                raise RuntimeError("{} is not an available primary key!".format(self.cleaned_data["primary_key"]))
        else:
            raise RuntimeError("This isn't valid!")

class EditFloorForm(forms.Form):
    name = forms.CharField(max_length=30, required=True)
    privacy = forms.BooleanField(label="Private?:", required=False) 
    number_of_stocks = forms.IntegerField(label="Maximum Number of Stocks (per player)", min_value=1, max_value=1000)
    permissiveness = forms.ChoiceField(choices=Floor.PERMISSIVENESS_CHOICES)
    stocks = StockChoiceField(label="Stocks")
    def apply(self, oFloor):
        oFloor.name = self.cleaned_data["name"]
        oFloor.permissiveness = self.cleaned_data["permissiveness"]
        oFloor.stocks = self.cleaned_data["stocks"]
        oFloor.num_stocks = self.cleaned_data["number_of_stocks"]
        oFloor.public = not self.cleaned_data["privacy"]
        oFloor.save()

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.widgets.PasswordInput())
    new_password = forms.CharField(widget=forms.widgets.PasswordInput())
    new_password_2 = forms.CharField(widget=forms.widgets.PasswordInput(), label="Confirm new password")
