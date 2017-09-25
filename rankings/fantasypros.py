import re
import lxml.html
import requests

from bs4 import BeautifulSoup
from lxml import etree
from rankings.models import Teams
from django.conf import settings

class FantasyProsData(object):

    def __init__(self):
        self.teamData = {}
        self.rosRankings = {}

    def process(self):
    	s = requests.session()
    	login = s.get('https://secure.fantasypros.com/accounts/login/')
    	login_html = lxml.html.fromstring(login.text)
    	hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

    	"""
    		Cleanup to dynamically find this later
    	"""
    	csrfToken = hidden_inputs[0].value

    	payload = {
    		'action': 'login',
    		'username': settings.FANTASY_PROS_USERNAME,
    		'password': settings.FANTASY_PROS_PASSWORD,
    		'csrfmiddlewaretoken': csrfToken
    	}

    	"""
			Log into FantasyPros and use lmxl to parse the dashboard/analysis rankings.
		"""
    	s.post('https://secure.fantasypros.com/accounts/login/', data=payload)
    	response = s.get(settings.FANTASY_PROS_DASHBOARD)
    	dashboard_html = lxml.html.fromstring(response.text)
    	rankings = dashboard_html.xpath(r'//tbody')

    	for tableElement in rankings[0]:
    		teamRanking = tableElement.find_class('col1')[0].text_content()
    		teamName = tableElement.find_class('col2')[0].text_content()

    		# Update database with this info
    		team = Teams.objects.get(name = teamName, league_year = settings.LEAGUE_YEAR)
    		team.current_roster_rank = teamRanking
    		team.save()