# This is the stocks app urlconf. It is named differently for speedier Vimming. 

from stocks import views
from django.conf.urls import url, patterns, include

urlpatterns = [
            url("^instructions/$", views.instructions, name="instructions"),
            url("^login/$", views.login, name="loginpage"),
            url("^thisisalongurlforloggingoutbutitdoesntmatterbcmagic/$", views.logout, name="mylogout"), 
            url("^auth/", include('django.contrib.auth.urls'), name="auth"),
            url("^$", views.index, name="home"), 
            url("^dashboard/$", views.dashboard, name="dashboard"),
            url("^createfloor/$", views.create_floor, name="createFloor"), 
            url("^joinfloor/$", views.join_floor, name="joinFloor"),
            url("^joinAFloor/([0-9]+)/$", views.join, name="join"), 
            url("^stockLookupURL/stock/(.+?)/$", views.stockLookup, name="lookup"), 
            url("^stockLookupURL/$", views.stockLookup, name="prefetch"), 
            url("^stockLookupURL/user/(?P<key>[0-9]+)/$", views.stockLookup, name="prefetch"), 
            url("^stockLookupURL/user/(?P<user>[A-Za-z0-9]+)/(?P<floor>[0-9]+)/$", views.stockLookup, name="prefetch"), 
            url("^thisCANbAEASAReallyHardURL/(?P<identifier>[A-Za-z0-9_]+)/(?P<player>[A-Za-z0-9]+)/$", views.renderStockWidgetJavascript, name="stockWidgetJavascript"), 
            url("^thisCANbAEASAReallyHardURL/(?P<identifier>[A-Za-z0-9_]+)/$", views.renderStockWidgetJavascript, name="stockWidgetJavascript"), 
            url("^trade/floor/(?P<pkFloor>[0-9]+)/$", views.trade, name="trade"), 
            url("^trade/floor/(?P<pkFloor>[0-9]+)/counter/(?P<pkCountering>[0-9]+)/$", views.trade, name="trade"), 
            url("^trade/player/(?P<pkPlayer>[0-9]+)/floor/(?P<pkFloor>[0-9]+)/$", views.trade, name="trade"), 
            url("^trade/floor/(?P<pkFloor>[0-9]+)/stock/(?P<pkStock>[0-9]+)/$", views.trade, name="trade"), 
            url("^playerFieldJavaScript/(?P<identifier>[A-Za-z0-9]+)/$", views.playerFieldJavascript, name="playerFieldJS"), 
            url("^userList/$", views.userList, name="users"), 
            url("^tradeFormJavaScript/$", views.tradeFormJavaScript, name="tradeFormJavaScript"), 
            url("^receivedTrade/(?P<pkTrade>[0-9]+)/$", views.receivedTrade, name="receivedTrade"),
            url("^youWillNeverGuessThisURLHAHahahhahaha/$", views.receivedTradeJavaScript, name="receivedTradeJavascript"), 
            url("^counterATrade/(?P<pkTrade>[0-9]+)/floor/(?P<floor>[0-9]+)/$", views.counterTrade, name="counterTrade"), 
            url("^acceptATrade/(?P<pkTrade>[0-9]+)/$", views.acceptTrade, name="acceptTrade"), 
            url("^rejectATrade/(?P<pkTrade>[0-9]+)/$", views.rejectTrade, name="rejectTrade"), 
            url("^deletePlayerFromFloor/pkPlayer/(?P<pkPlayer>[0-9]+)/$", views.deletePlayer, name="deletePlayer"),
            url("^acceptAStockSuggestion/pkSuggestion/(?P<pkSuggestion>[0-9]+)/(?P<delete>del/?)?", views.acceptSuggestion, name="acceptStock"), 
            url("^user/(?P<pkUser>[0-9]+)/$", views.userPage, name="userPage"), 
            url("^editUser/$", views.editAccount, name="editUser"), 
            url("^editFloor/floor/(?P<pkFloor>[0-9]+)/$", views.editFloor, name="editFloor"), 
            url("^changePassword/$", views.changePassword, name="myChangePassword"), 
            url("^deleteAFloor/floor/(?P<pkFloor>[0-9]+)/$", views.deleteFloor, name="deleteFloor"), 
            url("^editFloorjavascript/floor/(?P<pkFloor>[0-9]+)/$", views.editFloorJavaScript, name="editFloorJS"), 
            url("^playerJSON/player/(?P<pkPlayer>[0-9]+)/$", views.playerJson, name="playerJson"), 
            url("^floorJSON/floor/(?P<pkFloor>[0-9]+)/$", views.floorJson, name="floorJson"), 
        ]


# I'm going to have to make forms for all these eventually. I guess I'll keep them here 
# so I have them.
#
# ^login/$ [name='login']
# ^logout/$ [name='logout']
# ^password_change/$ [name='password_change']
# ^password_change/done/$ [name='password_change_done']
# ^password_reset/$ [name='password_reset']
# ^password_reset/done/$ [name='password_reset_done']
# ^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$ [name='password_reset_confirm']
# ^reset/done/$ [name='password_reset_complete']
