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
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.3'}
        self.source_url = 'http://www.wm.pollub.pl/pl/studenci/plany-zajec'
        self.check_loop.start()
        self.old_url = ""
        logging.info("[PSS] Program intialized")

    @tasks.loop(seconds=10)
    async def check_loop(self):
        await self.check_updates()

    @commands.command()
    async def set_channel(self, context):
        self.main_channel = context
        logging.info("[PSS] Channel has been selected", )
        await context.send("Channel has been selected")
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
        if not hasattr(self, 'main_channel'):
            return

        logging.info("[PSS] Check executed")
        new_url = self.get_url()
        if new_url != self.old_url:
            if self.old_url == "":
                self.old_url = new_url
                logging.info("[PSS] Initialized; first URL has been found")
                return

            logging.info("[PSS] Found new schedule")
            await self.main_channel.send(
                "Hej, jakiś cwel wrzucił właśnie nową wersję planu zajęć mechatro\n\n"
                "Nowa wersja planu zajęć:\n" + new_url + "\n\n"
                "Stara wersja planu zajęć:\n" + self.old_url
            )

            self.old_url = new_url

    def get_url(self): 
        html = requests.get(self.source_url, allow_redirects=True)
        soup = BeautifulSoup(html.content, 'html.parser')
        tag = soup.find("a", string="ME III rok")

        return tag['href']

load_dotenv()
bot.add_cog(PollubScheduleSearcher())
bot.run(os.getenv('TOKEN'))