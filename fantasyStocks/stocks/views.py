from django.shortcuts import render, redirect
from django.http import HttpResponse
from stocks import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, "dashboard.html", {"email" : request.user.email})
# Create your views here.
def index(request):
    # If you're already logged in...
    if request.user:
        return HttpResponsePermanentRedirect(reverse("dashboard"))
    # If we got here through a submission...
    if request.method == "POST":
        if request.POST.get("password1", None) != None:
            form = forms.RegistrationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(username=form.cleaned_data["email"], email=form.cleaned_data["email"], password=form.cleaned_data["password1"])
                user.save()
                user = authenticate(username=form.cleaned_data["email"], password=form.cleaned_data["password1"])
                login(request, user)
                return HttpResponsePermanentRedirect(reverse("dashboard"))
            else:
                if form._errors.get("already_exists", None):
                    error = form._errors["already_exists"]
                elif form._errors.get("dontmatch", None):
                    error = form._errors["dontmatch"]
                else:
                    error = "There was an error with your registration"
                return render(request, "index.html", {"registrationError" : error, "registrationForm" : form, "loginForm" : forms.LoginForm()})
        elif request.POST.get("password", None) != None:
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]
                user = authenticate(username=email, password=password)
                login(request, user)
                return HttpResponsePermanentRedirect(reverse("dashboard"))
    else:
        regForm = forms.RegistrationForm()
        logForm = forms.LoginForm()
        return render(request, "index.html", {"loginForm" : logForm,  "registrationForm" : regForm})
def instructions(request):
    return render(request, "instructions.html")
