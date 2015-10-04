# This is the stocks app urlconf. It is named differently for speedier Vimming. 

from stocks import views
from django.conf.urls import url, patterns

urlpatterns = [
            url("^instructions/$", views.instructions, name="instructions"),
            url("^$", views.index, name="home"), 
        ]
