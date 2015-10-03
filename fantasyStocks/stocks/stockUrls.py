# This is the stock urlconf.

from stocks import views
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse

urlpatterns = [
            url("instructions/", views.instructions, name="instructions"),
            url("index/", views.index, name="homepage"),
            url("^/$", RedirectView.as_view(url=reverse("homepage"), permanent=True)), 
        ]
