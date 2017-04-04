from stocks import forms
from stocks.models import Player, Floor, Stock, Trade, StockSuggestion, TradeError
from stocks.admin import checkForBug

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, hashers
from django.contrib.auth.views import logout_then_login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from urllib import request as py_request
import json

FLOOR_USER = User.objects.get(groups__name__exact="Floor")
# IMPORTANT: Keep jQuery at the beginning or else it won't load first and bad stuff will happen.
STANDARD_SCRIPTS = ["//code.jquery.com/jquery-1.11.3.min.js"]

@login_required
def dashboard(request):
    scripts =  STANDARD_SCRIPTS + [static("common.js"), static("floorTabs.js"), reverse("dashboardJavaScript")]
    players = Player.objects.filter(user=request.user)
    # If this user isn't a member of any floors...
    if not players:
        return redirect(reverse("joinFloor"), permanent=False)
    return render(request, "dashboard.html", 
            {
                "user": request.user, 
                "players": players,
                "floors": [i.floor for i in Player.objects.filter(user=request.user)], 
                "scripts": scripts,
            })

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("dashboard"))
    if request.method == "POST":
        # Don't tell anyone I did this. Basically, the RegistrationForm has something called "password1" in it because you have to confirm your
        # password. I use this to find out whether the RegistrationForm or the LoginForm has been submitted.
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
                return render(request, "index.html", {"loginForm" : form,  "registrationForm" : forms.RegistrationForm()})
        return HttpResponseRedirect(form.cleaned_data["nextPage"])
    else:
        regForm = forms.RegistrationForm()
        logForm = forms.LoginForm()
        # If we were redirected here because of a `login_required`...
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
    scripts = STANDARD_SCRIPTS + [static("common.js"), static("createFloor.js")]
    outputDict = {"scripts": scripts}
    if request.method == "POST":
        form = forms.FloorForm(request.POST)
        if form.is_valid():
            floor = form.save()
            floor.owner = request.user
            newPlayer = Player.objects.create(user=request.user, floor=floor)
            newFloorPlayer = Player.objects.create(user=FLOOR_USER, floor=floor)
            newFloorPlayer.save()
            floor.floorPlayer = newFloorPlayer
            floor.save()
            for s in floor.stocks.all():
                newFloorPlayer.stocks.add(s)
            return redirect(reverse("dashboard"), permanent=False)
        else:
            outputDict["form"] = form
            return render(request, "createFloor.html", outputDict)
    else:
        outputDict["form"] = forms.FloorForm()
        return render(request, "createFloor.html", outputDict)


@login_required
def join_floor(request):
    scripts = STANDARD_SCRIPTS + [static("common.js"), reverse("joinFloorJavaScript"), static("typeahead.bundle.js")]
    if not request.POST:
        form = forms.JoinFloorForm()
    else:
        form = forms.JoinFloorForm(request.POST)
        if form.is_valid():
            return redirect(reverse("join", args=(Floor.objects.get(name=form.cleaned_data["floor_name"]).pk, )))
        else:
            pass
    return render(request, "joinFloor.html", {"form": form, "scripts": scripts,
        "floors_exist": len([f for f in Floor.objects.all() if not f in [p.floor for p in Player.objects.filter(user=request.user)]]) > 0})

@login_required
def join(request, pkFloor):
    """
    This is the page that actually tells the server to add the player to the floor in the database. 
    There's nothing on here for the user to actually see. 
    """
    floor = Floor.objects.get(pk=pkFloor)
    # Make sure that we don't add the same person to a floor more than once.
    if not Player.objects.filter(user=request.user, floor=floor).exists():
        player = Player.objects.create(user=request.user, floor=floor)
        player.save()
    return redirect(reverse("dashboard"), permanent=False)


@login_required
def trade(request, pkPlayer=None, pkStock=None, pkFloor=None, pkCountering=None):
    outputDict = {}
    outputDict["request"] = request
    if request.POST:
        form = forms.TradeForm(request.POST)
        if form.is_valid(pkFloor=pkFloor, user=request.user, pkCountering=pkCountering):
            form.clean()
            form.to_trade(pkFloor=pkFloor, user=request.user)
            if pkCountering:
                Trade.objects.get(pk=pkCountering).delete()
            return redirect(reverse("dashboard"), permanent=False)
        else:
            if pkCountering:
                outputDict["countering"] = Trade.objects.get(pk=pkCountering)
            outputDict["form"] = form
    elif not (pkPlayer or pkStock or pkFloor):
        raise RuntimeError("You need to at least pass in a floor")
    # If you came here from clicking to trade with a player...
    elif pkPlayer and pkFloor and not pkStock:
        otherPlayer = Player.objects.get(pk=pkPlayer)
        init_dict = {}
        if otherPlayer.user == request.user:
            otherPlayer = None
        else:
            init_dict["other_user"] = otherPlayer.user.username
        outputDict["form"] = forms.TradeForm(initial=init_dict)
    # If you came here from clicking to trade a stock...
    elif pkStock and pkFloor and not pkPlayer:
        floor = Floor.objects.get(pk=pkFloor)
        stocks = [Stock.objects.get(pk=pkStock)]
        stocks_string = ",".join([s.symbol for s in stocks])
        try:
            # stocks__id means look for something with this id in the "stocks" many-to-many field. 
            otherPlayer = Player.objects.get(floor=floor, stocks__id=pkStock)
            if otherPlayer.user == request.user:
                outputDict["form"] = forms.TradeForm(initial={"user_stocks": stocks_string})
            else:
                outputDict["form"] = forms.TradeForm(initial={"other_user": otherPlayer.user.username, "other_stocks": stocks_string})
        except Player.DoesNotExist:
            outputDict["form"] = forms.TradeForm(initial={"other_stocks": stocks_string})
    elif pkFloor and pkCountering:
        raise RuntimeError("got floor and pk")
    else:
        raise RuntimeError("You passed in the wrong arguments")
    outputDict["floor"] = Floor.objects.get(pk=pkFloor)
    outputDict["userPlayer"] = Player.objects.get(user=request.user, floor=outputDict["floor"])
    checkForBug()
    return render(request, "trade.html", outputDict)

@login_required
def editAccount(request):
    user = request.user
    if request.POST:
        form = forms.UserEditingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard", permanent=False)
        else:
            pass
    else:
        formDict = {"primary_key": user.pk}
        formDict["username"] = user.username
        formDict["last_name"] = user.last_name
        formDict["first_name"] = user.first_name
        formDict["email"] = user.email
        form = forms.UserEditingForm(formDict)
    return render(request, "editUser.html", {"form": form, "players": Player.objects.filter(user=user)})

@login_required
def editFloor(request, pkFloor=None):
    scripts = STANDARD_SCRIPTS + [static("common.js"), reverse("editFloorJS", kwargs={"pkFloor": pkFloor})]
    if not pkFloor:
        raise RuntimeError("You didn't pass in a floor.")
    try:
        floor = Floor.objects.get(pk=pkFloor)
    except Floor.DoesNotExist:
        raise RuntimeError("{} is not an available floor!".format(pkFloor))
    if request.POST:
        form = forms.EditFloorForm(request.POST)
        if form.is_valid():
            form.apply(floor)
            # Remove all the removed stocks from the floor's players
            for player in Player.objects.filter(floor=floor):
                for s in player.stocks.all():
                    if not s in floor.stocks.all():
                        player.stocks.remove(s)
                player.save()
            return redirect(reverse("dashboard"))
    form = forms.EditFloorForm({"name": floor.name, "stocks": ",".join([s.symbol for s in floor.stocks.all()]), "permissiveness": floor.permissiveness, "privacy": not floor.public, "number_of_stocks": floor.num_stocks})
    return render(request, "editFloor.html", {"form": form, "floor": floor, "scripts": scripts, "absolute_join_url": request.build_absolute_uri(reverse("join", args=[floor.pk]))})

@login_required
def changePassword(request):
    if request.POST:
        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["new_password_2"] == form.cleaned_data["new_password"]:
                old_password = form.cleaned_data["old_password"]
                new_password = form.cleaned_data["new_password"]
                user = request.user
                if hashers.check_password(old_password, user.password):
                    user.password = hashers.make_password(new_password)
                    user.save()
                    return redirect(reverse("dashboard"), permanent=False)
                else:
                    form.add_error("old_password", "Your old password is wrong!")
            else:
                form.add_error("new_password_2", "Your passwords don't match!")
    else:
        form = forms.ChangePasswordForm()
    return render(request, "changePassword.html", {"form": form})

@login_required
def receivedTrade(request, pkTrade):
    trade = Trade.objects.get(pk=pkTrade)
    form = forms.ReceivedTradeForm(trade.toFormDict())
    try:
        errors = trade.verify()
    except TradeError as e:
        form.add_error(None, str(e))
    return render(request, "trade.html", {"form" : form,
        "received": True,
        "trade": trade,
        "floor": trade.floor, 
        "userPlayer": trade.recipient})

@login_required
def rejectTrade(request, pkTrade):
    Trade.objects.get(pk=pkTrade).delete()
    return redirect(reverse("dashboard"), permanent=False)

@login_required
def acceptTrade(request, pkTrade):
    trade = Trade.objects.get(pk=pkTrade)
    trade.accept()
    checkForBug(obj=trade)
    return redirect(reverse("dashboard"), permanent=False)

@login_required
# pkFloor is here for the sake of the JavaScript on the page. I don't use it in any Python code.
def counterTrade(request, pkTrade, pkFloor):
    trade = Trade.objects.get(pk=pkTrade)
    form = forms.TradeForm(initial=trade.toFormDict())
    # TODO: There is too much repitition for these template variables. I need to find a better way. 
    outputDict = {"form": form,
            "request": request,
            "countering": trade, 
            "floor": trade.floor, 
            "userPlayer": trade.recipient}
    checkForBug(obj=trade)
    return render(request, "trade.html", outputDict)

@login_required
def userPage(request, pkUser):
    user = User.objects.get(pk=pkUser)
    scripts =  STANDARD_SCRIPTS + [static("common.js"), static("floorTabs.js")]
    outputDict = {"user": user, "players": Player.objects.filter(user=user), "scripts": scripts}
    return render(request, "userPage.html", outputDict)


def playerFieldJavascript(request, identifier):
    return render(request, "playerField.js", {"id" : identifier})

def receivedTradeJavaScript(request):
    return render(request, "receivedTrade.js", {})

def userList(request):
    return HttpResponse(json.dumps([{"username": u.username if u.username else u.email, "email": u.email} for u in User.objects.all()]), content_type="text/json")

def stockLookup(request, query=None, key=None, user=None, pkFloor=None):
    # This if branch is depricated
    if query:
        STOCK_URL = "http://dev.markitondemand.com/Api/v2/Lookup/json?input={}"
        return HttpResponse(py_request.urlopen(STOCK_URL.format(query)), content_type="text/json")
    elif key:
        # If given a primary key, this function returns a JSON list of all the stocks that that player owns.
        return HttpResponse(json.dumps([s.format_for_json() for s in Player.objects.get(pk=key).stocks.all()]), content_type="text/json")
    elif user and pkFloor:
        # If given a username and a floor, this returns all the stocks for the player of that user on that floor.
        floor = Floor.objects.get(pk=pkFloor)
        player = Player.objects.get(user__username=user, floor=floor)
        if player.isFloor() and not floor.permissiveness == "closed":
            return redirect(static("stocks.json"))
        return HttpResponse(json.dumps([i.format_for_json() for i in player.stocks.all()]))
    else:
        return redirect(static("stocks.json"), permanent=True)

def renderStockWidgetJavascript(request, identifier=None, pkPlayer=None):
    if not identifier:
        raise RuntimeError("You didn't pass in a valid identifier. God only knows how that happened.")
    if not pkPlayer:
        return render(request, "stockWidget.js", {"class_name" : forms.StockWidget().HTML_CLASS, "id": identifier})
    return render(request, "stockWidget.js", {"id": identifier, "class_name" : forms.StockWidget().HTML_CLASS, "player": player })
def tradeFormJavaScript(request):
    return render(request, "trade.js")
def tradeCommonJavaScript(request):
    return render(request, "tradeCommon.js")
def editFloorJavaScript(request, pkFloor=None):
    return render(request, "editFloor.js", {"floor": Floor.objects.get(pk=pkFloor)})

@login_required
def deletePlayer(request, pkPlayer=None):
    if not pkPlayer:
        raise RuntimeError("You didn't give me a player. God only knows how that happened.")
    else:
        Player.objects.get(pk=pkPlayer).delete()
        return redirect(reverse("dashboard"), permanent=False)

@login_required
def acceptSuggestion(request, pkSuggestion=None, delete=None):
    if not pkSuggestion:
        raise RuntimeError("You didn't give me a suggestion. God only knows how that happened.")
    elif delete:
        StockSuggestion.objects.get(pk=pkSuggestion).delete()
    else:
        StockSuggestion.objects.get(pk=pkSuggestion).accept()
    return redirect(reverse("dashboard"), permanent=False)

def deleteFloor(request, pkFloor=None):
    if not pkFloor:
        raise RuntimeError("This should never happen. You didn't give a floor")
    Floor.objects.get(pk=pkFloor).delete()
    return redirect(reverse("dashboard"), permanent=False)

def playerJson(request, pkPlayer=None):
    if not pkPlayer:
        raise RuntimeError("You need to supply a player to get information!")
    else:
        return HttpResponse(Player.objects.get(pk=pkPlayer).to_json())

def floorJSON(request, pkFloor=None):
    if not pkFloor:
        raise RuntimeError("You need to supply a floor to get information!")
    else:
        return HttpResponse(json.dumps(Floor.objects.get(pk=pkFloor).to_json()))
def joinFloorJavaScript(request):
    return render(request, "joinFloor.js")

def floorsJSON(request):
    return HttpResponse(json.dumps([{"name": i.name} for i in Floor.objects.filter(public=True) if not Player.objects.filter(user=request.user, floor=i)]))

def dashboardJavaScript(request):
    return render(request, "dashboard.js")

def getStockPrice(request, symbol=None):
    if not symbol:
        raise RuntimeError("You need to give a symbol, fool!")
    stock = Stock.objects.get(symbol=symbol)
    if not stock.has_current_price():
        stock.update()
    return HttpResponse(json.dumps({"price": float(stock.price), "change": float(stock.change), "symbol": stock.symbol}))

def getStockBoardJavaScript(request):
    return render(request, "stockBoard.js")

def getPlayersOnFloor(request, pkFloor=None):
    if not pkFloor:
        raise RuntimeError("You need to pass in a floor, fool!")
    return HttpResponse(json.dumps([{"username": i.get_name()} for i in Player.objects.filter(floor__pk=pkFloor)]))
