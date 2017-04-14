import dateutil.parser
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from stocks.models import *
from stocksApi.models import SessionId

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


def viewUser(request, pkUser = None):
    return JsonResponse(getObject(User, pkUser), safe=False)

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
                p["receivedTrades"] = list(filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                       p["receivedTrades"]))
                p["sentTrades"] = list(filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                       p["sentTrades"]))
    else:
        retval["receivedTrades"] = list(filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                retval["receivedTrades"]))
        retval["sentTrades"] =  list(filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                retval["sentTrades"]))

    return JsonResponse(retval, safe=False)

def viewStock(request, pkStock = None):
    return JsonResponse(getObject(Stock, pkUser), safe=False)

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

def viewFloor(request, pkFloor = None):
    return JsonResponse(getObject(Floor, pkFloor), safe=False)

def createUser(request):
    data = request.POST
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

    newUser = User.objects.create_user(**userDict)
    return JsonResponse(userJSON(newUser))

def createPlayer(request):
    post = request.POST
    get = request.GET
    playerData = {}
    for badData in ["points", "isFloor", "sentTrades", "receivedTrades", "isFloorOwner"]:
        if post.get(badData, None):
            return getParamError(badData)

    user = getUser(request)
    if not user:
        return getPermError()
    else:
        if not user.pk == post["user"]:
            return getPermError()
        playerData["user"] = user

    if post.get("floor", None):
        playerData["floor"] = Floor.object.get(pk=post["floor"])
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

def createTrade(request):
    tradeData = {}
    get = request.GET
    post = request.POST
    user = getUser(request)
    if not user:
        return getPermError()

    try:
        tradeData["sender"] = Player.objects.get(post["senderPlayer"])
        tradeData["recipient"] = Player.objects.get(post["recipientPlayer"])
        if post.get("date", None):
            tradeData["date"] = dateutil.parser.parse(post["date"])
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
    for i in senderStocks:
        newTrade.senderStocks.objects.add(i)

    for i in recipientStocks:
        newTrade.recipientStocks.objects.add(i)

    newTrade.save()
    try:
        newTrade.verify()
    except (TradeError, RuntimeError) as e:
        return getError(str(e))

    newTrade.refresh_from_db()
    return JsonResponse(newTrade.toJSON())


def createStockSuggestion(request):
    post = request.POST
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

    newSuggestion = StockSuggestions(**suggestionData)
    newSuggestion.save()
    newSuggestion.refresh_from_db()
    return JsonResponse(newSuggestion.toJSON())

def createFloor(request):
    post = request.POST
    get = request.GET
    floorData = {}

    if not post.get("name", None):
        return getParamError("name")
    else:
        floorData["name"] = post["name"]

    if type(post.get("stocks", [])) != type([]):
        return getParamError("stocks")
    else:
        floorData["stocks"] = [Stock.objects.get(pk=i) for i in post.get("stocks", [])]

    if not post.get("permissiveness", "") in ["Permissive", "Open", "Closed"]:
        return getParamError("permissiveness")
    else:
        floorData["permissiveness"] = post["permissiveness"]

    if not post.get("owner", None):
        return getParamError("owner")
    else:
        floorData["owner"] = User.objects.get(post["owner"])

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
    newFloor.refresh_from_db()

    return JsonResponse(newFloor.toJSON())

def getToken(request):
    if not (request.POST.get('username', None) and request.POST.get('password', None)):
        return getParamError()
    username = request.POST["username"]
    password = request.POST["password"]
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "That username doesn't exist"})

    if not user.check_password(password):
        return JsonResponse({"error": "That password is wrong"})

    newSessionId = SessionId(associated_user=user)
    newSessionId.save()
    return JsonResponse({"sessionId": newSessionId.id_string, "user": userJSON(user)})

def registerToken(request):
    post = request.POST
    get = request.GET
    user = getUser()
    if not user:
        return getPermError()

    if not post.get("registrationToken", None):
        return getParamError("registrationToken")
    else:
        token = AndroidToken(user=user, token=post["registrationToken"])
        token.save()
        return JsonResponse({"success": "Your registration id was successfully registered with {}".format(user.username)})

def deregisterToken(request):
    post = request.POST
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

