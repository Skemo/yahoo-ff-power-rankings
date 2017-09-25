import operator

from rankings.models import ScoringLog, Teams, PowerRankingsData
from django.db.models import Avg, StdDev
from collections import OrderedDict

class CalcRankings(object):

    def __init__(self):
        self.teamData = Teams.objects.all()
        self.ovwScore = {}
        self.conScore = {}
        self.avgScore = {}
        self.winScore = {}
        self.rosScore = {}

        for team in self.teamData:
            self.ovwScore[team.id] = 0
            self.conScore[team.id] = 0
            self.avgScore[team.id] = 0
            self.winScore[team.id] = 0
            self.rosScore[team.id] = 0

    def generateRankings(self, week=1):
        """
        Calculate total OVW
        """

        for leagueWeek in range(1, int(week) + 1):
            scoringData = ScoringLog.objects.select_related('team').filter(week=leagueWeek
                ).extra(select={'ovw_rank': 'rank() over(order by points_scored)'})

            for score in scoringData:
                self.ovwScore[score.team.id] += score.ovw_rank

        """
        Calculate consistency score
        """

        leagueAvg = ScoringLog.objects.select_related('team').aggregate(Avg('points_scored'))

        for team in self.teamData:
            teamAvg = ScoringLog.objects.filter(team=team).aggregate(Avg('points_scored'))
            
            """
            Store team average, wins, and roster score
            """

            self.avgScore[team.id] = round(teamAvg['points_scored__avg'], 2)
            self.winScore[team.id] = team.wins
            self.rosScore[team.id] = team.current_roster_rank

            teamStd = ScoringLog.objects.filter(team=team).aggregate(
                StdDev('points_scored', sample=True))

            if round(teamAvg['points_scored__avg'], 2) - round(leagueAvg['points_scored__avg'], 2) == 0:
                self.conScore[team.id] = 0
            else:
                self.conScore[team.id] = (round(teamAvg['points_scored__avg'], 2) - round(
                    leagueAvg['points_scored__avg'], 2)) / round(teamStd['points_scored__stddev'],2)
                if round(self.conScore[team.id],1) == -0.0:
                    self.conScore[team.id] = 0
                else:
                    self.conScore[team.id] = round(self.conScore[team.id],1)
            
        """
        Store power rankings source data
        """
        rankedOvw = OrderedDict(sorted(self.ovwScore.items(), key=lambda t: t[1], reverse=True))
        
        for ovwRank in range(0,len(rankedOvw)):
            teamInfo = rankedOvw.popitem(last=False)
            team = Teams.objects.get(id=teamInfo[0])
            rank = ovwRank+1

            obj, created = PowerRankingsData.objects.update_or_create(
                team = team, week = week, defaults = {'team': team, 'ovw_rank': rank})

        rankedCon = OrderedDict(sorted(self.conScore.items(), key=lambda t: t[1], reverse=True))

        for conRank in range(0,len(rankedCon)):
            teamInfo = rankedCon.popitem(last=False)
            team = Teams.objects.get(id=teamInfo[0])
            rank = conRank+1

            obj, created = PowerRankingsData.objects.update_or_create(
                team = team, week = week, defaults = {'team': team, 'con_rank': rank})

        rankedAvg = OrderedDict(sorted(self.avgScore.items(), key=lambda t: t[1], reverse=True))

        for avgRank in range(0,len(rankedAvg)):
            teamInfo = rankedAvg.popitem(last=False)
            team = Teams.objects.get(id=teamInfo[0])
            rank = avgRank+1

            obj, created = PowerRankingsData.objects.update_or_create(
                team = team, week = week, defaults = {'team': team, 'avg_rank': rank})        

        rankedWin = OrderedDict(sorted(self.winScore.items(), key=lambda t: t[1], reverse=True))
        
        for winRank in range(0,len(rankedWin)):
            teamInfo = rankedWin.popitem(last=False)
            team = Teams.objects.get(id=teamInfo[0])
            rank = winRank+1

            obj, created = PowerRankingsData.objects.update_or_create(
                team = team, week = week, defaults = {'team': team, 'win_rank': rank})   

        rankedRos = OrderedDict(sorted(self.rosScore.items(), key=lambda t: t[1], reverse=True))

        for rosRank in range(0,len(rankedRos)):
            teamInfo = rankedRos.popitem(last=False)
            team = Teams.objects.get(id=teamInfo[0])
            rank = rosRank+1

            obj, created = PowerRankingsData.objects.update_or_create(
                team = team, week = week, defaults = {'team': team, 'ros_rank': rank})           

        """
        Calculate power rankings for week
        """
        rankingData = PowerRankingsData.objects.filter(week=week)

        for ranks in rankingData:
            rankTotal = (3*ranks.win_rank) + ranks.ovw_rank + ranks.avg_rank + ranks.con_rank + ranks.ros_rank
            powerRanking = rankTotal / 5

            obj, created = PowerRankingsData.objects.update_or_create(
                team = ranks.team, week = week, defaults = {'team': ranks.team, 'pow_rank': powerRanking})     

        powerRanks = PowerRankingsData.objects.select_related('team').filter(week=week).order_by('pow_rank')

        print('RANKINGS PROCESSED FOR WEEK {}'.format(week))
        
        for rank in powerRanks:
            print('{} ({})'.format(rank.team.name,rank.pow_rank))