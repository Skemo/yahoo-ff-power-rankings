import myql
import json
from yahoo_oauth import OAuth1
from myql.utils import pretty_json, pretty_xml
from django.conf import settings

from rankings.models import Teams, ScoringLog


class YahooData(object):

    def __init__(self):
        self.teamData = {}
        self.pointsScored = {}
        self.oauth = OAuth1(None, None, from_file='./rankings/credentials.json')
        self.yql = myql.MYQL(format='json', oauth=self.oauth)
        self.current_week = 0

    def processTeamData(self):
        """
        Team data
        """
        teams = self.yql.raw_query(
            'select * from fantasysports.leagues.standings where league_key="{}"'.format(settings.LEAGUE_KEY), format='json')
        jsonTeams = json.loads(pretty_json(teams.content))

        teamInfo = jsonTeams['query']['results']['league']['standings']['teams']['team']

        self.current_week = jsonTeams['query']['results']['league']['current_week']

        for team in teamInfo:
            self.teamData[team['team_key']] = {'season': team['team_points']['season'], 'wins': 0, 'team_name': team['name'], 'logo': team[
                'team_logos']['team_logo']['url'], 'manager': team['managers']['manager']['nickname']}

    def processScoringData(self):
        """
        Get points per week for each team and wins
        """
        for week in range(1, int(self.current_week)):
            """
            Get results from each week
            """
            scoreboard = self.yql.raw_query(
                'select scoreboard from fantasysports.leagues.scoreboard where league_key="{}" and week={}'.format(settings.LEAGUE_KEY, week), format='json')
            jsonScoreboard = json.loads(pretty_json(scoreboard.content))
            matchups = jsonScoreboard['query']['results'][
                'league']['scoreboard']['matchups']['matchup']
            weeklyScores = {}

            for matchup in matchups:
                weeklyScores[matchup['teams']['team'][0]['team_key']] = matchup[
                    'teams']['team'][0]['team_points']['total']
                weeklyScores[matchup['teams']['team'][1]['team_key']] = matchup[
                    'teams']['team'][1]['team_points']['total']
                self.teamData[matchup['winner_team_key']]['wins'] += 1

            self.pointsScored[week] = weeklyScores

    def process(self):
        """
        Grab updated fantasy data from Yahoo!
        """
        self.processTeamData()
        self.processScoringData()

        """
        Update team database
        """
        for team in self.teamData:
            obj, created = Teams.objects.update_or_create(
                team_key=team, league_year=self.teamData[team]['season'],
                defaults={'team_key': team, 'name': self.teamData[team][
                    'team_name'], 'league_year': self.teamData[team]['season'], 'wins': self.teamData[team]['wins'], 'manager': self.teamData[team][
                    'manager'], 'logo': self.teamData[team]['logo']}
            )

        """
        Update scoring log database
        """
        for teamScores in self.pointsScored:
            for team in self.pointsScored[teamScores]:
                week = teamScores
                teamObj = Teams.objects.get(team_key=team)
                score = self.pointsScored[teamScores][team]

                obj, created = ScoringLog.objects.update_or_create(
                    team=teamObj, week=week,
                    defaults={'team': teamObj, 'week': week, 'points_scored': score}
                )