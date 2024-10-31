from ANNIEMUSIC.core.bot import MOON
from ANNIEMUSIC.core.dir import dirr
from ANNIEMUSIC.core.git import git
from ANNIEMUSIC.core.userbot import Userbot
from ANNIEMUSIC.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = MOON()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
HELPABLE = {}
