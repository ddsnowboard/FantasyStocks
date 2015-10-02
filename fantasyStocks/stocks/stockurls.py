# This is the stock urlconf.

from stocks import views
from django.conf.urls import url
from django.shortcuts import redirect

urlpatterns = [
        url("index.html", views.index),
        # url("", redirect("index.html", permanent=True)), 
        ]
