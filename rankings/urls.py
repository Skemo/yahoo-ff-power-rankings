from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', DisplayRankings.as_view(), name='display-rankings'),
]