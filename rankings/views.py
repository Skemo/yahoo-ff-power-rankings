from django.shortcuts import render
from django.views.generic import View

from .models import Teams

class DisplayRankings(View):
    """
    Display rankings for current week.
    """
    template_name = 'display_rankings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = Teams.objects.all()

        return context
