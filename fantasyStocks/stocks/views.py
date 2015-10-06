from django.shortcuts import render
from django.http import HttpResponse
from stocks import forms

# Create your views here.
def index(request):
    regForm = forms.RegistrationForm()
    logForm = forms.LoginForm()
    return render(request, "index.html", {"loginForm" : logForm,  "registrationForm" : regForm})
def instructions(request):
    return render(request, "instructions.html")
