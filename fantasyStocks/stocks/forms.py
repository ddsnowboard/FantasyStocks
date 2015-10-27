from django.conf.urls.static import static
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from stocks.models import Floor, Stock, StockAPIError
from django.core.exceptions import ValidationError
import sys

class StockWidget(forms.widgets.TextInput):
    """
    This widget allows the user to select any stock, whether or not 
    it's in the database. It returns a list of Stock objects (it will create
    the new objects within itself) so it can be used with a ManyToMany field.
    """
    CLASS = "stockBox"
    class Media:
        js = ("//code.jquery.com/jquery-1.11.3.min.js", "typeahead.bundle.js", "stockWidget.js")
    def __init__(self, attrs=None):
        forms.widgets.TextInput.__init__(self, attrs if attrs else {})
        self.attrs["class"] = StockWidget.CLASS
    def to_python(self, value):
        raise Exception("This is an exception. Th")
        out = []
        for i in value.split(","):
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
class FloorForm(forms.ModelForm):
    def validate(self, value, model_instance):
        print(self.validators, file=sys.stderr)
        forms.ModelForm.validate(self, value, model_instance)
    class Meta:
        model = Floor
        fields = ["name", "stocks", "permissiveness"]
        widgets = {"stocks": StockWidget}
