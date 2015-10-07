from django.shortcuts import render
from django.http import HttpResponse
from stocks import forms
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    # If we got here through a submission...
    if request.method == "POST":
        if request.POST.get("password1", None):
            form = forms.RegistrationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(username=form.cleaned_data["email"], email=form.cleaned_data["email"], password=form.cleaned_data["password"])
                user.save()
            else:
                if form._errors["already_exists"]:
                    error = form._errors["already_exists"]
                else:
                    error = "There was an error with your registration"
        elif request.POST["password"]:
            form = forms.LoginForm(request.POST)
    else:
        regForm = forms.RegistrationForm()
        logForm = forms.LoginForm()
        return render(request, "index.html", {"loginForm" : logForm,  "registrationForm" : regForm})
def instructions(request):
    return render(request, "instructions.html")
