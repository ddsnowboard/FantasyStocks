# This is the stocks app urlconf. It is named differently for speedier Vimming. 

from stocks import views
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
            path("instructions/", views.instructions, name="instructions"),
            path("login/", views.login, name="loginpage"),
            path("thisisalongurlforloggingoutbutitdoesntmatterbcmagic/", views.logout, name="mylogout"), 
            path("auth/", include('django.contrib.auth.urls'), name="auth"),
            path("", views.index, name="home"), 
            path("dashboard/", views.dashboard, name="dashboard"),
            path("createfloor/", views.create_floor, name="createFloor"), 
            path("joinfloor/", views.join_floor, name="joinFloor"),
            path("joinAFloor/floor/<int:pkFloor/", views.join, name="join"), 
            path("stockLookupURL/", views.stockLookup, name="prefetch"), 
            path("stockLookupURL/user/<int:pkPlayer>/", views.stockLookup, name="prefetch"), 
            path("stockLookupURL/user/<username>/<int:pkFloor>/", views.stockLookup, name="prefetch"), 
            path("thisCANbAEASAReallyHardURL/<identifier>/<int:pkPlayer>/", views.renderStockWidgetJavascript, name="stockWidgetJavascript"), 
            path("thisCANbAEASAReallyHardURL/<identifier>/", views.renderStockWidgetJavascript, name="stockWidgetJavascript"), 
            path("trade/floor/<int:pkFloor>/", views.trade, name="trade"), 
            path("trade/floor/<int:pkFloor>/counter/<int:pkCountering>/", views.trade, name="trade"), 
            path("trade/player/<int:pkPlayer>/floor/<int:pkFloor>/", views.trade, name="trade"), 
            path("trade/floor/<int:pkFloor>/stock/<int:pkStock>/", views.trade, name="trade"), 
            path("playerFieldJavaScript/<identifier>/", views.playerFieldJavascript, name="playerFieldJS"), 
            path("userList/", views.userList, name="users"), 
            path("tradeFormJavaScript/", views.tradeFormJavaScript, name="tradeFormJavaScript"), 
            path("receivedTrade/<int:pkTrade>/", views.receivedTrade, name="receivedTrade"),
            path("youWillNeverGuessThisURLHAHahahhahaha/", views.receivedTradeJavaScript, name="receivedTradeJavascript"), 
            path("counterATrade/<int:pkTrade>/floor/<int:pkFloor>/", views.counterTrade, name="counterTrade"), 
            path("acceptATrade/<int:pkTrade>/", views.acceptTrade, name="acceptTrade"), 
            path("rejectATrade/<int:pkTrade>/", views.rejectTrade, name="rejectTrade"), 
            path("deletePlayerFromFloor/pkPlayer/<int:pkPlayer>/", views.deletePlayer, name="deletePlayer"),
            path("acceptAStockSuggestion/pkSuggestion/<int:pkSuggestion>/", views.acceptSuggestion, name="acceptStock"), 
            path("user/<int:pkUser>/", views.userPage, name="userPage"), 
            path("editUser/", views.editAccount, name="editUser"), 
            path("editFloor/floor/<int:pkFloor>/", views.editFloor, name="editFloor"), 
            path("changePassword/", views.changePassword, name="myChangePassword"), 
            path("deleteAFloor/floor/<int:pkFloor>/", views.deleteFloor, name="deleteFloor"), 
            path("editFloorjavascript/floor/<int:pkFloor>/", views.editFloorJavaScript, name="editFloorJS"), 
            path("playerJSON/player/<int:pkPlayer>/", views.playerJson, name="playerJson"), 
            path("floorJSON/floor/<int:pkFloor>/", views.floorJSON, name="floorJSON"), 
            path("tradeCommonJavaScript/", views.tradeCommonJavaScript, name="tradeCommonJavaScript"), 
            path("joinFloorJavaScript/", views.joinFloorJavaScript, name="joinFloorJavaScript"), 
            path("getFloorsJSON/", views.floorsJSON, name="floorsJson"), 
            path("dashboardJavaScript/", views.dashboardJavaScript, name="dashboardJavaScript"), 
            path("getStockPrice/stock/<symbol>/", views.getStockPrice, name="stockPrice"), 
            path("stockBoardJavaScript/", views.getStockBoardJavaScript, name="stockBoardJavaScript"), 
            path("floorPlayers/floor/<int:pkFloor>/", views.getPlayersOnFloor, name="floorPlayers"),
            path("blankPage/", lambda request: HttpResponse(""), name="blank"),
        ]


# I'm going to have to make forms for all these eventually. I guess I'll keep them here 
# so I have them.
#
# ^login/ [name='login']
# ^logout/ [name='logout']
# ^password_change/ [name='password_change']
# ^password_change/done/ [name='password_change_done']
# ^password_reset/ [name='password_reset']
# ^password_reset/done/ [name='password_reset_done']
# ^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/ [name='password_reset_confirm']
# ^reset/done/ [name='password_reset_complete']
