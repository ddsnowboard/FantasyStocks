from django.conf.urls import url

from . import views

urlpatterns = [
    url("user/view/([0-9]+)", views.viewUser, name="viewUser"),
    url("user/view/", views.viewUser, name="viewAllUsers"),
    
    url("player/view/([0-9]+)", views.viewPlayer, name="viewPlayer"),
    url("player/view/", views.viewPlayer, name="viewAllPlayers"),
    
    url("stock/view/([0-9]+)", views.viewStock, name="viewStock"),
    url("stock/view/", views.viewStock, name="viewAllStocks"),
    
    url("trade/view/([0-9]+)", views.viewTrade, name="viewTrade"),
    url("trade/view/", views.viewTrade, name="viewAllTrades"),
    
    url("stockSuggestion/view/([0-9]+)", views.viewStockSuggestion, name="viewStockSuggestion"),
    url("stockSuggestion/view/", views.viewStockSuggestion, name="viewAllStockSuggestions"),
    
    url("floor/view/([0-9]+)", views.viewFloor, name="viewFloor"),
    url("floor/view/", views.viewFloor, name="viewAllFloors"),

    url("auth/getKey", views.getToken, name="getKey"),
]
