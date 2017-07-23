from django.conf.urls import url
from django.http import JsonResponse
from json import dumps

from . import views

urlpatterns = [
    url("user/view/([0-9]+)", views.viewUser, name="viewUser"),
    url("user/view/", views.viewUser, name="viewAllUsers"),
    url("user/create/", views.createUser, name="createUser"), 
    
    url("player/view/([0-9]+)", views.viewPlayer, name="viewPlayer"),
    url("player/view/", views.viewPlayer, name="viewAllPlayers"),
    url("player/create/", views.createPlayer, name="createPlayer"), 
    
    url("stock/view/([0-9]+)", views.viewStock, name="viewStock"),
    url("stock/view/", views.viewStock, name="viewAllStocks"),
    
    url("trade/view/([0-9]+)", views.viewTrade, name="viewTrade"),
    url("trade/view/", views.viewTrade, name="viewAllTrades"),
    url("trade/create/", views.createTrade, name="createTrade"), 
    
    url("stockSuggestion/view/([0-9]+)", views.viewStockSuggestion, name="viewStockSuggestion"),
    url("stockSuggestion/view/", views.viewStockSuggestion, name="viewAllStockSuggestions"),
    url("stockSuggestion/create/", views.createStockSuggestion, name="createStockSuggestion"), 
    
    url("floor/view/([0-9]+)", views.viewFloor, name="viewFloor"),
    url("floor/view/", views.viewFloor, name="viewAllFloors"),

    # "createFloor" was already taken
    url("floor/create/", views.createFloor, name="ApiCreateFloor"), 

    url("trade/accept/([0-9]+)", views.acceptTrade, name="acceptTrade"),
    url("trade/decline/([0-9]+)", views.declineTrade, name="declineTrade"),

    url("stockSuggestion/accept/([0-9]+)", views.acceptStockSuggestion, name="acceptStockSuggestion"),
    url("stockSuggestion/reject/([0-9]+)", views.rejectStockSuggestion, name="rejectStockSuggestion"),

    url("auth/getKey", views.getToken, name="getKey"),

    url("android/register/", views.registerAndroidToken, name="registerToken"), 
    url("android/deregister/", views.deregisterAndroidToken, name="deregisterToken"), 

    url("test/", views.tester, name="tester")
]
