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
            self.source = await self.queue.get()

            await self._ctx.send('**Now Playing:** {}'.format(self.source.title))
            self.voice_client.play(self.source, after=self.unlock_player)
            
            await self.event.wait()
            
    
    async def stop(self):
        while(not self.queue.empty()):
            await self.queue.get()

        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
    
    def unlock_player(self, error=None):
        if error:
            raise AudioControllerError(str(error))
        
        self.event.set()
    
    def skip(self):
        if self.voice_client and self.source:
            self.voice_client.stop()
