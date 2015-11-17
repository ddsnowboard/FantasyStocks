from random import randint
from django.conf.urls.static import static
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy, reverse
from stocks.models import Floor, Stock, StockAPIError
from django.core.exceptions import ValidationError
from stocks.models import Floor
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
        print(self.attrs, file=sys.stderr)
    def to_python(self, value):
            s = Stock.objects.get(symbol=i)
            if not s:
                s = Stock(symbol=i)
                try:
                    s.update()
                except StockAPIError:
                    raise ValidationError
                s.save()
            out.append(s)
    def validate(self, value):
        return True
    def _media(self):
        js = ["//code.jquery.com/jquery-1.11.3.min.js",
        "typeahead.bundle.js",]
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
        print("rendering {}".format(super(StockWidget, self).render(name, value, attrs)), file=sys.stderr)
        return super(StockWidget, self).render(name, value, attrs)

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
    stocks = StockChoiceField(label="Stocks")
    permissiveness = forms.ChoiceField(label="Permissiveness", choices=Floor.PERMISSIVENESS_CHOICES)
    def __init__(self, *args, user=None, floor=None, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        if user and floor:
            stocks = StockChoiceField(label="Stocks")
        elif not user and not floor:
            pass
        else:
            raise RuntimeError("You have to either pass in a user and a floor, or neither.")
    def is_valid(self):
        return super(FloorForm, self).is_valid()
    def save(self):
        floor = Floor(name=self.cleaned_data['name'], permissiveness=self.cleaned_data['permissiveness'])
        floor.save()
        for i in self.cleaned_data['stocks']:
            floor.stocks.add(i)
        floor.save()
        return floor

# TODO: Make this work
class PlayerField(forms.Field):
    def __init__(self, floor=None, other=None, *args, **kwargs):
        forms.Field.__init__(self, *args, **kwargs)


class TradeForm(forms.Form):
    USER_STOCK_PICKER_ID = "id_user_stock_picker"
    OTHER_STOCK_PICKER_ID = "id_other_stock_picker"
    other_picker = PlayerField(label="Other Player")
    user_stock_picker = StockChoiceField(label="Your Stocks")
    other_stock_picker = StockChoiceField(label="Other player's stocks")
    def __init__(self, *args, user=None, other=None, floor=None, **kwargs):
        super(TradeForm, self).__init__(*args, **kwargs)
        print("initializing fields", file=sys.stderr)
        self.other_picker = PlayerField(floor=floor, other=other)
        self.user_stock_picker = StockChoiceField(label="Your Stocks", widget=StockWidget(prefetchPlayerPk=user.pk, attrs={"id": self.USER_STOCK_PICKER_ID}))
        self.other_stock_picker = StockChoiceField(label="{}'s Stocks".format(other.user.username), widget=StockWidget(prefetchPlayerPk=other.pk, attrs={"id": self.OTHER_STOCK_PICKER_ID}))
