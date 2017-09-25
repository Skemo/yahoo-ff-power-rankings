from django.core.management.base import BaseCommand, CommandError
from rankings.calcrankings import CalcRankings

class Command(BaseCommand):

    def handle(self, *args, **options):

        rankWeek = input("Process rankings for week: ")
        
        calcRankings = CalcRankings()
        calcRankings.generateRankings(week=rankWeek)