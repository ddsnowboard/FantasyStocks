from django.shortcuts import render, redirect
from django.http import HttpResponse
from stocks import forms
from stocks.models import Player, Floor, Stock
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import logout_then_login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import escape
from urllib import request as py_request
import json
import sys
import csv

STANDARD_SCRIPTS = ["//code.jquery.com/jquery-1.11.3.min.js"]

@login_required
def dashboard(request):
    # IMPORTANT: Keep jQuery at the beginning or else it won't load first and bad stuff will happen.
    scripts =  STANDARD_SCRIPTS + [static("dashboard.js")]
    players = Player.objects.filter(user=request.user)
    if not players:
        return redirect(reverse("joinFloor"), permanent=False)
    return render(request, "dashboard.html", 
            {
                "user": request.user, 
                "players": players,
                "floors": [i.floor for i in Player.objects.filter(user=request.user)], 
                "scripts" : scripts,
            })

# Create your views here.
def index(request):
    # If you're already logged in...
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("dashboard"))
    # If we got here through a submission...
    if request.method == "POST":
        if "password1" in request.POST:
            form = forms.RegistrationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(username=form.cleaned_data["username"], email=form.cleaned_data["email"], password=form.cleaned_data["password1"])
                user.save()
                user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
                login(request, user)
            else:
                error = form.get_errors()
                return render(request, "index.html", {"registrationError" : error, "registrationForm" : form, "loginForm" : forms.LoginForm()})
        elif "password" in request.POST:
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                else:
                    return render(request, "index.html", {"loginError": "That username or password doesn't exist", "loginForm" : form,  "registrationForm" : forms.RegistrationForm()})
        return HttpResponseRedirect(form.cleaned_data["nextPage"])
    # If there is no POST from a prior submission...
    else:
        regForm = forms.RegistrationForm()
        logForm = forms.LoginForm()
        # If we were redirected here from login_required...
        if "next" in request.GET:
            for i in (regForm, logForm):
                i.fields["nextPage"].initial = request.GET["next"]
        return render(request, "index.html", {"loginForm" : logForm,  "registrationForm" : regForm})

def instructions(request):
    return render(request, "instructions.html")

@login_required
def logout(request):
    return logout_then_login(request)

@login_required
def create_floor(request):
    if request.method == "POST":
        form = forms.FloorForm(request.POST)
        if form.is_valid():
            floor = form.save()
            floor.owner = request.user
            floor.save()
            newPlayer = Player.objects.create(user=request.user, floor=floor)
            newPlayer.save()
            return redirect(reverse("dashboard"), permanent=False)
        else:
            return render(request, "createFloor.html", variableDict)
    else:
        form = forms.FloorForm()
        return render(request, "createFloor.html", {"form": form})


@login_required
def join_floor(request):
    scripts = STANDARD_SCRIPTS + [static("joinFloor.js")]
    floors = list(Floor.objects.all())
    for i in Player.objects.filter(user=request.user):
        floors.remove(i.floor)
    return render(request, "joinFloor.html", {"floors": floors, "scripts": scripts})

@login_required
def join(request, floorNumber):
    player = Player.objects.create(user=request.user, floor=Floor.objects.get(pk=floorNumber))
    player.save()
    return redirect(reverse("dashboard"), permanent=False)


@login_required
def trade(request, player=None, stock=None, floor=None):
    outputDict = {}
    outputDict["request"] = request
    if request.POST:
        form = forms.TradeForm(request.POST)
        if form.is_valid(floor=floor, user=request.user):
            form.clean()
            # TODO: Create a trade object and go somewhere else. I'm not there yet
            return HttpResponse("Worked! <pre>{}</pre>".format(escape(form.cleaned_data)))
        else:
            outputDict["form"] = form
    elif not (player or stock or floor):
        raise RuntimeError("You need to at least pass in a floor")
    elif player and floor and not stock:
        otherPlayer = Player.objects.get(pk=player)
        init_dict = {}
        if otherPlayer.user == request.user:
            otherPlayer = None
        else:
            init_dict["other_user"] = otherPlayer.user.username
        outputDict["form"] = forms.TradeForm(initial=init_dict)
    elif stock and floor and not player:
        floor = Floor.objects.get(pk=floor)
        # stocks__id means look for something with this id in the "stocks" many-to-many field. 
        stocks = [Stock.objects.get(pk=stock)]
        stocks_string = ",".join([s.symbol for s in stocks])
        try:
            otherPlayer = Player.objects.get(floor=floor, stocks__id=stock)
            if otherPlayer.user == request.user:
                outputDict["form"] = forms.TradeForm(initial={"user_stocks": stocks_string})
            else:
                outputDict["form"] = forms.TradeForm(initial={"other_user": otherPlayer.user.username, "other_stocks": stocks_string})
        except Player.DoesNotExist:
            # This should give you the floor player, but I haven't implemented that yet. 
            outputDict["form"] = forms.TradeForm(initial={"other_stocks": stocks_string})
    else:
        raise RuntimeError("You passed in the wrong arguments")
    return render(request, "trade.html", outputDict)

def playerFieldJavascript(request, identifier):
    return render(request, "playerField.js", {"id" : identifier})

def userList(request):
    return HttpResponse(json.dumps([{"username": u.username if u.username else u.email, "email": u.email} for u in User.objects.all()]), content_type="text/json")

def stockLookup(request, query=None, key=None, user=None, floor=None):
    # I don't really use this branch anymore, but I might need it. 
    if query:
        STOCK_URL = "http://dev.markitondemand.com/Api/v2/Lookup/json?input={}"
        return HttpResponse(py_request.urlopen(STOCK_URL.format(query)), content_type="text/json")
    # This is almost always the part that runs.
    elif key:
        return HttpResponse(json.dumps([s.format_for_json() for s in Player.objects.get(pk=key).stocks.all()]), content_type="text/json")
    elif user and floor:
        return HttpResponse(json.dumps([i.format_for_json() for i in Player.objects.get(user__username=user, floor=floor).stocks.all()]))
    else:
        return redirect(static("stocks.json"), permanent=True)

def renderStockWidgetJavascript(request, identifier=None, player=0):
    """
    player is the primary key of the player in a database, not a Player object,
    since it has to come from a URL. 
    """
    if not identifier:
        raise RuntimeError("You didn't pass in a valid identifier. God only knows how that happened.")
    if not player:
        return render(request, "stockWidget.js", {"class_name" : forms.StockWidget().HTML_CLASS, "id": identifier})
    player = int(player)
    # The id is coming from here. Make it give the right id (eg, "id_other_stock_picker"). I'm not sure how. Ask the form? 
    # Pass it in the URL?
    return render(request, "stockWidget.js", {"id": identifier, "class_name" : forms.StockWidget().HTML_CLASS, "player": player })
def tradeFormJavaScript(request):
    return render(request, "trade.js")
