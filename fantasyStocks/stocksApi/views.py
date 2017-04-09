from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from stocks.models import *
from stocksApi.models import SessionId

def getDNEError():
    return JsonResponse({"error": "That object could not be found"})

def getAuthError():
    return JsonResponse({"error": "Your session id is old or never existed. You should get a new one"})

def getPermError():
    return JsonResponse({"error": "You don't have permission to see that"})

def getParamError():
    return JsonResponse({"error": "You gave the wrong parameters"})

def getUser(request):
    sessionId = request.GET.get("sessionId", None)
    if not sessionId:
        return None
    try:
        user = SessionId.objects.get(id_string=sessionId).associated_user
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
    retval = getObject(Player, pkUser)
    user = None
    if not request.GET.get("sessionId", None):
        sessionId = SessionId.objects.filter(id_string=request.GET["sessionId"]).order_by("-exp_date")
        if sessionId:
            sessionId = sessionId[0]
            if not sessionId.is_expired():
                user = sessionId.associated_user
            else:
                sessionId.delete()

    if type(retval) == type([]):
        for p in retval:
            playerUser = Player.get(pk=p['id'])
            if playerUser == user:
                continue
            else:
                filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                       p["receivedTrades"])
                filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                       p["sentTrades"])
    else:
        filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                retval["receivedTrades"])
        filter(lambda pkT: tradeInvolvesUser(Trade.objects.get(pk=pkT), playerUser),
                retval["sentTrades"])

    return JsonResponse(retval, safe=False)

def viewStock(request, pkStock = None):
    return JsonResponse(getObject(Stock, pkUser), safe=False)

def viewTrade(request, pkTrade = None):
    user = getUser(request)
    if not user:
        return getPermError()
    if not pkTrade:
        trades = [o.toJson() for o in Trade.objects.filter(Q(sender=user) | Q(recipient=user))]
        return JsonResponse(trades)

    if not user:
        return getPermError()
    try:
        oTrade = Trade.objects.get(id=pkTrade)
    except ObjectDoeNotExist:
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
    except ObjectDoeNotExist:
        return getDNEError()
    if user == suggestion.floor.owner:
        return JsonResponse(getObject(StockSuggestion, pkSuggestion), safe=False)
    else:
        return getPermError()

def viewFloor(request, pkFloor = None):
    return JsonResponse(getObject(Floor, pkFloor), safe=False)

def getToken(request):
    if not (request.POST.get('username', None) and request.POST.get('password', None)):
        return getParamError()
    username = request.POST["username"]
    password = request.POST["password"]
    user = User.objects.filter(username=username)
    if not user:
        return JsonResponse({"error": "That username doesn't exist"})
    else:
        user = user[0]

    if not user.check_password(password):
        return JsonResponse({"error": "That password doesn't exist"})

    newSessionId = SessionId(associated_user=user)
    newSessionId.save()
    return JsonResponse({"sessionId": newSessionId.id_string, "user": userJSON(user)})
