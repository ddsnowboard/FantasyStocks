from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from stocks.models import *
from stocksApi.models import SessionId

# Create your views here.

def getAuthError():
    return JsonResponse({"error": "Your session id is old or never existed. You should get a new one"})

def getPermError():
    return JsonResponse({"error": "You don't have permission to see that"})

def getParamError():
    return JsonResponse({"error": "You gave the wrong parameters"})



def getObject(klass, pk):
    if pk == None:
        if klass == User:
            return [userJSON(u) for u in klass.objects.all()]
        else:
            return [o.toJSON() for o in klass.objects.all()]
    else:
        try:
            obj = klass.get(pk=pk)
            if klass == User:
                return userJSON(obj)
            else:
                return obj.toJSON()
        except ObjectDoeNotExist:
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
    return JsonResponse(getObject(Trade, pkTrade), safe=False)

def viewStockSuggestion(request, pkSuggestion = None):
    return JsonResponse(getObject(StockSuggestion, pkSuggestion), safe=False)

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
