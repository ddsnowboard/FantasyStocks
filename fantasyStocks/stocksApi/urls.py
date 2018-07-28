from django.urls import path
from django.http import JsonResponse
from json import dumps

from . import views

urlpatterns = [
    path("user/view/<int:pkUser>/", views.viewUser, name="viewUser"),
    path("user/view/", views.viewUser, name="viewAllUsers"),
    path("user/create/", views.createUser, name="createUser"), 
    
    path("player/view/<int:pkPlayer>/", views.viewPlayer, name="viewPlayer"),
    path("player/view/", views.viewPlayer, name="viewAllPlayers"),
    path("player/create/", views.createPlayer, name="createPlayer"), 
    
    path("stock/view/<int:pkStock>/", views.viewStock, name="viewStock"),
    path("stock/view/", views.viewStock, name="viewAllStocks"),
    
    path("trade/view/<int:pkTrade>/", views.viewTrade, name="viewTrade"),
    path("trade/view/", views.viewTrade, name="viewAllTrades"),
    path("trade/create/", views.createTrade, name="createTrade"), 
    
    path("stockSuggestion/view/<int:pkSuggestion>", views.viewStockSuggestion, name="viewStockSuggestion"),
    path("stockSuggestion/view/", views.viewStockSuggestion, name="viewAllStockSuggestions"),
    path("stockSuggestion/create/", views.createStockSuggestion, name="createStockSuggestion"), 
    
    path("floor/view/<int:pkFloor>/", views.viewFloor, name="viewFloor"),
    path("floor/view/", views.viewFloor, name="viewAllFloors"),

    # "createFloor" was already taken
    path("floor/create/", views.createFloor, name="ApiCreateFloor"), 

    path("trade/accept/<int:pkTrade>/", views.acceptTrade, name="acceptTrade"),
    path("trade/decline/<int:pkTrade>/", views.declineTrade, name="declineTrade"),

    path("stockSuggestion/accept/<int:pkSuggestion>/", views.acceptStockSuggestion, name="acceptStockSuggestion"),
    path("stockSuggestion/reject/<int:pkSuggestion>/", views.rejectStockSuggestion, name="rejectStockSuggestion"),

    path("auth/getKey", views.getToken, name="getKey"),

    path("android/register/", views.registerAndroidToken, name="registerToken"), 
    path("android/deregister/", views.deregisterAndroidToken, name="deregisterToken"), 

    path("test/", views.tester, name="tester")
]
