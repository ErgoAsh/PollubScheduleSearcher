import requests
import os
import logging

from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from bs4 import BeautifulSoup

logging.basicConfig(
    filename='console.log', 
    encoding='utf-8', 
    level=logging.DEBUG,
    format='%(asctime)s %(message)s'
)

bot = commands.Bot(command_prefix='!!')
bot.remove_command('check')

class PollubScheduleSearcher(commands.Cog):
    def __init__(self):
        self.headers = {'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/88.0.4324.150 Safari/537.3'}
        self.source_url = 'https://wm.pollub.pl/studenci/plany-zajec'
        self.check_loop.start()
        self.old_url = ""
        self.channels = []
        logging.info("[PSS] Program intialized")

    @tasks.loop(seconds=10)
    async def check_loop(self):
        await self.check_updates()

    @commands.command()
    async def add_channel(self, context):
        if (context not in self.channels):
            self.channels.append(context)
            logging.info("[PSS] Channel has been added")
            await context.send("Channel has been added")
            await self.check_updates()

    @commands.command()
    async def remove_channel(self, context):
        if (context in self.channels):
            self.channels.remove(context)
            logging.info("[PSS] Channel has been removed")
            await context.send("Channel has been removed")
            await self.check_updates()

    @commands.command()
    async def check(self, context):
        old_url = self.old_url if self.old_url != "" else "NO URL"
        await context.send(
            "Aktualna wersja planu zajęć:\n" + self.get_url() + "\n\n"
            "Zapisana wersja planu zajęć:\n" + old_url
        )
        logging.info("[PSS] Manual check executed")

    async def check_updates(self):
        logging.info("[PSS] Check executed")
        new_url = self.get_url()

        if (new_url == "NO URL"):
            return 

        if new_url == self.old_url:
            return

        if self.old_url == "":
            self.old_url = new_url
            logging.info("[PSS] Initialized; first URL has been found")
            return

        logging.info("[PSS] Found new schedule")
        for channel in self.channels:
            await channel.send(
                "Hej, jakiś cwel wrzucił właśnie nową wersję planu zajęć mechatro\n\n"
                "Nowa wersja planu zajęć:\n" + new_url + "\n\n"
                "Stara wersja planu zajęć:\n" + self.old_url
            )

        self.old_url = new_url

    def get_url(self): 
        html = requests.get(self.source_url, allow_redirects=True)
        soup = BeautifulSoup(html.content, 'html.parser')
        tag = soup.find("a", string="ME III rok")

        if (tag is None):
            return "NO URL"
        else:
            return tag['href'] or ""

load_dotenv()
bot.add_cog(PollubScheduleSearcher())
bot.run(os.getenv('TOKEN'))