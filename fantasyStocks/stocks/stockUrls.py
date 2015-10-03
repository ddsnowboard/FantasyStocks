# This is the stock urlconf.

from stocks import views
from django.conf.urls import url
from django.views.generic.base import RedirectView

urlpatterns = [
        url("index.html", views.index),
        url("$", RedirectView.as_view(url="index.html", permanent=True)), 
        ]
