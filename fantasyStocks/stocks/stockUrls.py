# This is the stocks app urlconf. It is named differently for speedier Vimming. 

from stocks import views
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

urlpatterns = [
            # url("instructions/", views.instructions, name="instructions"),
            # url("index/", views.index, name="homepage"),
            url("^$", RedirectView.as_view(url=reverse_lazy("homepage"), permanent=True)), 
        ]
