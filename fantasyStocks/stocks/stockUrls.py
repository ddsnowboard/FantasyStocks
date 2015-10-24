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
            url("^stockLookupURL/(.)+?/$", views.stockLookup, name="lookup"), 
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
