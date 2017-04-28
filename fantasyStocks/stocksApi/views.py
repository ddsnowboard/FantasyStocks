from django.views.decorators.csrf import csrf_exempt
import dateutil.parser
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import IntegrityError
from django.http import JsonResponse
from stocks.models import *
from stocksApi.models import SessionId, AndroidToken
from json import loads

def getError(message):
    return JsonResponse({"error": message})


def getDNEError():
    return getError("That object could not be found")

def getAuthError():
    return getError("Your session id is old or never existed. You should get a new one")

def getPermError():
    return getError("You don't have permission to see that")

def getParamError(lacking = None):
    retval = getError("You gave the wrong parameters." + 
                      ("{} is/are missing".format(lacking)) if lacking else "")
    return JsonResponse({"error": "You gave the wrong parameters", "wrongParams": lacking})


def getUser(request):
    sessionId = request.GET.get("sessionId", None)
    if not sessionId:
        return None
    try:
        id = SessionId.objects.get(id_string=sessionId)
        if not id.is_expired():
            return id.associated_user
        else:
            id.delete()
            return None
    except ObjectDoesNotExist:
        return None


def getObject(klass, pk):
    if pk == None:
        if klass == User:
            return [userJSON(u) for u in klass.objects.all()]
        else:
            return [o.toJSON() for o in klass.objects.all()]
    else:
        try:
            obj = klass.objects.get(pk=pk)
            if klass == User:
                return userJSON(obj)
            else:
                return obj.toJSON()
        except ObjectDoesNotExist:
            return {"error": "That object could not be found"}


def tradeInvolvesUser(oTrade, oUser):
    if oUser == None:
        return False
    return oTrade.sender.user == oUser or oTrade.recipient.user == oUser


@csrf_exempt
def viewUser(request, pkUser = None):
    return JsonResponse(getObject(User, pkUser), safe=False)

@csrf_exempt
def viewPlayer(request, pkPlayer = None):
    # A user shouldn't be privy to other users' trades.
    retval = getObject(Player, pkPlayer)
    user = getUser(request)

    if type(retval) == type([]):
        for p in retval:
            playerUser = Player.objects.get(pk=p['id'])
            if playerUser == user:
                continue
            else:
                p["receivedTrades"] = list(filter(lambda t: tradeInvolvesUser(Trade.objects.get(pk=t["id"]), user),
                       p["receivedTrades"]))
                p["sentTrades"] = list(filter(lambda t: tradeInvolvesUser(Trade.objects.get(pk=t["id"]), user),
                       p["sentTrades"]))
    else:
        retval["receivedTrades"] = list(filter(lambda t: tradeInvolvesUser(Trade.objects.get(pk=t["id"]), user),
                retval["receivedTrades"]))
        retval["sentTrades"] =  list(filter(lambda t: tradeInvolvesUser(Trade.objects.get(pk=t["id"]), user),
                retval["sentTrades"]))

    return JsonResponse(retval, safe=False)

@csrf_exempt
def viewStock(request, pkStock = None):
    return JsonResponse(getObject(Stock, pkStock), safe=False)

@csrf_exempt
def viewTrade(request, pkTrade = None):
    user = getUser(request)
    if not user:
        return getPermError()
    if not pkTrade:
        trades = [o.toJSON() for o in Trade.objects.filter(Q(sender__user=user) | Q(recipient__user=user))]
        return JsonResponse(trades, safe=False)

    if not user:
        return getPermError()
    try:
        oTrade = Trade.objects.get(id=pkTrade)
    except ObjectDoesNotExist:
        return getDNEError()
    if tradeInvolvesUser(oTrade, user):
        return JsonResponse(getObject(Trade, pkTrade), safe=False)
    else:
        return getPermError()

@csrf_exempt
def viewStockSuggestion(request, pkSuggestion = None):
    user = getUser(request)
    if not user:
        return getPermError()
    if not pkSuggestion:
        suggestions = StockSuggestion.objects.filter(floor__owner=user)
        return JsonResponse(suggestions)

    try:
        suggestion = StockSuggestion.objects.get(id=pkSuggestion)
    except ObjectDoesNotExist:
        return getDNEError()
    if user == suggestion.floor.owner:
        return JsonResponse(getObject(StockSuggestion, pkSuggestion), safe=False)
    else:
        return getPermError()

@csrf_exempt
def viewFloor(request, pkFloor = None):
    user = getUser(request)
    userPk = user.pk if user else -1
    floors = getObject(Floor, pkFloor)
    if not pkFloor:
        floors = list(filter(lambda x: x["public"] or x["owner"]["id"] == userPk, floors))
    return JsonResponse(floors, safe=False)

@csrf_exempt
def createUser(request):
    data = loads(request.body.decode("UTF-8"))
    userDict = {}
    if data.get("players", None):
        return getParamError("players")
    if data.get("email", None):
        userDict["email"] = data["email"]
    if data.get("password", None):
        userDict["password"] = data["password"]
    else:
        return getParamError("password")

    if data.get("username", None):
        userDict["username"] = data["username"]
    else:
        return getParamError("username")

    try:
        newUser = User.objects.create_user(**userDict)
    except IntegrityError:
        return getError("That username is already taken")
    return JsonResponse(userJSON(newUser))

@csrf_exempt
def createPlayer(request):
    post = loads(request.body.decode("UTF-8"))
    get = request.GET
    playerData = {}
    for badData in ["points", "isFloor", "sentTrades", "receivedTrades", "isFloorOwner"]:
        if post.get(badData, None):
            return getParamError(badData)

    user = getUser(request)
    if not user:
        return getPermError()
    else:
        postedPk = post.get("user", -1)
        if not user.pk == postedPk:
            return getPermError()
        playerData["user"] = user

    if post.get("floor", None):
        playerData["floor"] = Floor.objects.get(pk=post["floor"])
    else:
        return getParamError("floor")

    if Player.objects.filter(**playerData).exists():
        return getError("That player already exists")

    newPlayer = Player(**playerData)
    if post.get("stocks", None):
        stockIds = post.get["stocks"]
        for id in stockIds:
            newPlayer.stocks.add(Stock.objects.get(pk=id))

    newPlayer.save()
    newPlayer.refresh_from_db()
    return JsonResponse(newPlayer.toJSON())

@csrf_exempt
def createTrade(request):
    tradeData = {}
    get = request.GET
    post = loads(request.body.decode("UTF-8"))
    user = getUser(request)
    if not user:
        return getPermError()

    try:
        tradeData["sender"] = Player.objects.get(pk=post["senderPlayer"])
        if not tradeData["sender"].user == user:
            return getPermError()
        tradeData["recipient"] = Player.objects.get(pk=post["recipientPlayer"])
        tradeData["floor"] = Floor.objects.get(pk=post["floor"])
        if post.get("date", None):
            return getError("You can't pass a date")
    except KeyError:
        return getParamError("senderPlayer or recipientPlayer")
    except ObjectDoesNotExist:
        return getError("One of those players does not exist")

    if type(post.get("senderStocks", "this is an impossible value")) != type([]):
        return getParamError("senderStocks")
    else:
        senderStocks = [Stock.objects.get(pk=i) for i in post["senderStocks"]]

    if type(post.get("recipientStocks", "this is an impossible value")) != type([]):
        return getParamError("recipientStocks")
    else:
        recipientStocks = [Stock.objects.get(pk=i) for i in post["recipientStocks"]]

    if not (senderStocks or recipientStocks):
        return getParamError("recipientStocks or senderStocks")

    newTrade = Trade(**tradeData)
    newTrade.save()
    for i in senderStocks:
        newTrade.senderStocks.add(i)

    for i in recipientStocks:
        newTrade.recipientStocks.add(i)

    newTrade.save()
    try:
        newTrade.verify()
    except (TradeError, RuntimeError) as e:
        return getError(str(e))

    newTrade.refresh_from_db()
    return JsonResponse(newTrade.toJSON())


@csrf_exempt
def createStockSuggestion(request):
    post = loads(request.body.decode("UTF-8"))
    get = request.GET
    suggestionData = {}

    user = getUser(request)
    if not user:
        return getAuthError()

    if not post.get("stock", None):
        return getParamError("stock")
    else:
        suggestionData["stock"] = Stock.objects.get(pk=post["stock"])
    
    if not post.get("requestingPlayer", None):
        return getParamError("requestingPlayer")
    else:
        suggestionData["requesting_player"] = Player.objects.get(pk=post["requestingPlayer"])

    if not post.get("floor", None):
        return getParamError("floor")
    else:
        suggestionData["floor"] = Floor.objects.get(pk=post["floor"])

    if not suggestionData["requesting_player"].floor == suggestionData["floor"]:
        return getError("That floor doesn't match the player")
    if not suggestionData["floor"].permissiveness == Floor.PERMISSIVE:
        return getError("That floor doesn't support StockSuggestions")
    if not suggestionData["requesting_player"].user == user:
        return getError("That player does not match the sessionId you gave.")

    newSuggestion = StockSuggestion(**suggestionData)
    if not newSuggestion.isValid():
        return getError("That data is not valid")
    newSuggestion.save()
    newSuggestion.refresh_from_db()
    return JsonResponse(newSuggestion.toJSON())

@csrf_exempt
def createFloor(request):
    post = loads(request.body.decode("UTF-8"))
    get = request.GET
    user = getUser(request)
    floorData = {}

    IMPOSSIBLE_VALUE = "impossible value"

    if post.get("floorPlayer", IMPOSSIBLE_VALUE) != IMPOSSIBLE_VALUE:
        return getError("You can't pass a floorPlayer")

    if not post.get("name", None):
        return getParamError("name")
    else:
        floorData["name"] = post["name"]

    if type(post.get("stocks", [])) != type([]):
        return getParamError("stocks")
    else:
        stocks = [Stock.objects.get(pk=i) for i in post.get("stocks", [])]

    if not post.get("permissiveness", "") in ["Permissive", "Open", "Closed"]:
        return getParamError("permissiveness")
    else:
        floorData["permissiveness"] = post["permissiveness"]

    if not stocks and floorData["permissiveness"] == "Closed":
        return getError("You must have stocks by default if the floor is closed")

    if not post.get("owner", None):
        return getParamError("owner")
    else:
        owner = User.objects.get(pk=post["owner"])
        if owner == user:
            floorData["owner"] = owner
        else:
            return getError("The sessionId you passed didn't match the user who owns the floor")

    try:
        floorData["public"] = post["public"]
        if type(floorData["public"]) != type(False):
            return getParamError("public")
    except KeyError:
        return getParamError("public")

    if not post.get("numStocks", None):
        return getParamError("numStocks")
    else:
        floorData["num_stocks"] = post["numStocks"]

    newFloor = Floor(**floorData)
    newFloor.save()
    for s in stocks:
        newFloor.stocks.add(s)
    newFloor.refresh_from_db()

    return JsonResponse(newFloor.toJSON())

@csrf_exempt
def acceptTrade(request, pkTrade):
    try:
        trade = Trade.objects.get(pk=pkTrade)
    except ObjectDoesNotExist:
        return getError("There was no trade with id {}".format(pkTrade))

    user = getUser(request)
    if not user:
        return getAuthError()
    if not trade.recipient.user == user:
        return getPermError()

    try:
        trade.accept()
        return JsonResponse({"success": "The trade was successfully accepted"})
    except Error as e:
        return getError("Something bad happened. Here's the error: {}".format(str(e)))

@csrf_exempt
def declineTrade(request, pkTrade):
    user = getUser(request)
    try:
        trade = Trade.objects.get(pk=pkTrade)
    except ObjectDoesNotExist:
        return getError("There was no trade with id {}".format(pkTrade))

    if not user:
        return getAuthError()
    if not trade.recipient.user == user:
        return getAuthError()

    try:
        trade.delete()
        return JsonResponse({"success": "The trade was successfully declined"})
    except Exception as e:
        return getError("Something bad happened. Here's the error: {}".format(str(e)))

@csrf_exempt
def acceptStockSuggestion(request, pkSuggestion):
    user = getUser(request)
    try:
        suggestion = StockSuggestion.objects.get(pk=pkSuggestion)
    except ObjectDoesNotExist:
        return getError("The StockSuggestion {} does not exist".format(pkSuggestion))
    if not suggestion.floor.owner == user:
        return getAuthError()
    suggestion.accept()
    return JsonResponse({"success": "The StockSuggestion was successfully accepted"})

@csrf_exempt
def rejectStockSuggestion(request, pkSuggestion):
    user = getUser(request)
    try:
        suggestion = StockSuggestion.objects.get(pk=pkSuggestion)
    except ObjectDoesNotExist:
        return getError("The StockSuggestion {} does not exist".format(pkSuggestion))
    if not suggestion.floor.owner == user:
        return getAuthError()
    suggestion.delete()
    return JsonResponse({"success": "The StockSuggestion was successfully rejected"})

@csrf_exempt
def getToken(request):
    post = loads(request.body.decode("UTF-8"))
    if not (post.get('username', None) and post.get('password', None)):
        return getParamError()
    username = post["username"]
    password = post["password"]
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "That username doesn't exist"})

    if not user.check_password(password):
        return JsonResponse({"error": "That password is wrong"})

    newSessionId = SessionId(associated_user=user)
    newSessionId.save()
    return JsonResponse({"sessionId": newSessionId.id_string, "user": userJSON(user)})

@csrf_exempt
def registerToken(request):
    post = loads(request.body.decode("UTF-8"))
    get = request.GET
    user = getUser(request)
    if not user:
        return getPermError()

    if not post.get("registrationToken", None):
        return getParamError("registrationToken")
    else:
        token = AndroidToken(user=user, token=post["registrationToken"])
        token.save()
        return JsonResponse({"success": "Your registration id was successfully registered with {}".format(user.username)})

@csrf_exempt
def deregisterToken(request):
    post = loads(request.body.decode("UTF-8"))
    get = request.GET
    user = getUser(request)
    if not user:
        return getPermError()

    if not post.get("registrationToken", None):
        return getParamError("registrationToken")
    else:
        token = AndroidToken.objects.get(token=post["registrationToken"])
        if not token.user == user:
            return getError("That token and your reigstration id don't match")
        else:
            token.delete()
        return JsonResponse({"success": "Your registration id was successfully deleted from {}".format(user.username)})


@csrf_exempt
def tester(request):
    return JsonResponse(loads(request.body.decode("UTF-8")) if request.body else dict(request.GET), safe=False)
