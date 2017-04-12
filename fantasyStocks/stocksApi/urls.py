from django.conf.urls import url

from . import views

urlpatterns = [
    url("user/view/([0-9]+)/", views.viewUser, name="viewUser"),
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
    url("floor/create/", views.createFloor, name="createFloor"), 

    url("auth/getKey", views.getToken, name="getKey"),

    url("android/register/", views.registerToken, name="registerToken"), 
    url("android/deregister/", views.deregisterToken, name="deregisterToken"), 
]
