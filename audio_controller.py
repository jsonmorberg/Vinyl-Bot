# Class to handle the queue and music playing
import asyncio
from async_timeout import timeout

class AudioControllerError(Exception):
    pass

class AudioController:
    def __init__(self, bot, ctx):
        self.bot = bot
        self._ctx = ctx

        self.voice_client = None
        self.source = None
        self.event = asyncio.Event()
        self.queue = asyncio.Queue()

        self.player = bot.loop.create_task(self.audio_player())
    
    async def audio_player(self):
        while True:
            self.event.clear()

            try:
                async with timeout(180):
                    self.source = await self.queue.get()

            except asyncio.TimeoutError:
                self.bot.loop.create_task(self.stop())
                return

            self.voice_client.play(self.source, after=self.next_song)
            await self.source.channel.send('**Now Playing:** {}'.format(self.source.title))
            await self.event.wait()
    
    async def stop(self):
        while(not self.queue.empty()):
            await self.queue.get()

        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
    
    def next_song(self, error=None):
        if error:
            raise AudioControllerError(str(error))
        
        self.event.set()
    
    def skip_song(self):
        if self.voice and self.source:
            self.voice_client.stop()
