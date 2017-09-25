from django.core.management.base import BaseCommand, CommandError
from rankings.yahoo import YahooData
from rankings.fantasypros import FantasyProsData

class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Process Yahoo! data -- query league info and update databases.
        """
        
        yahooData = YahooData()
        yahooData.process()

        """
        Scrape FantasyPros for the rest of season ranks.
        """
        prosData = FantasyProsData()
        prosData.process()