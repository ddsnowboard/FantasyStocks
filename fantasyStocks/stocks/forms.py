from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100)
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput)
    nextPage = forms.CharField(label="next page", max_length=30, widget=forms.HiddenInput(), initial=reverse_lazy("dashboard"))
class RegistrationForm(forms.Form):
    # The order of this constant matters. Tripping `already_exists` doesn't make 
    # any sense if `dontmatch` has already been tripped. 
    POSSIBLE_ERRORS = ("dontmatch", "already_exists")
    email = forms.EmailField(label="Email", max_length=100)
    password1 = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm", max_length=50, widget=forms.PasswordInput)
    nextPage = forms.CharField(label="next page", max_length=30, widget=forms.HiddenInput(), initial=reverse_lazy("dashboard"))
    def is_valid(self):
        if not super(RegistrationForm, self).is_valid():
            return False
        if User.objects.filter(email=self.cleaned_data["email"]).exists():
            self._errors["already_exists"] = "That email is already taken"
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
