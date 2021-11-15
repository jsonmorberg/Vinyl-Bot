
import discord
import yt_dlp
import asyncio
import functools

# Class to download youtube audio and return filenames
class AudioSource(discord.PCMVolumeTransformer):

    YTDL_FORMAT_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0' 
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, search, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        partial =  functools.partial(cls.ytdl.extract_info, search, download=False)
        data = await loop.run_in_executor(None, partial)

        #process once to get entries from search
        processed_data = None
        if 'entries' in data:
            for entry in data['entries']:
                if entry:
                    processed_data = entry
                    break
        else:
            processed_data = data

        if processed_data is None:
                    raise Exception("No result that matches '{}'".format(search))

        url = processed_data['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, url, download=True)
        data = await loop.run_in_executor(None, partial)

        #process again for first entry in search
        web_data = None
        if 'entries' in data:
            while web_data is None:
                try:
                    web_data = data['entries'].pop(0)
                except IndexError:
                    raise Exception("No result that matches '{}'".format(search))
        else:
            web_data = data

        if processed_data is None:
                    raise Exception("No result that matches '{}'".format(search))

        filename = processed_data['title'] if stream else cls.ytdl.prepare_filename(processed_data)
        return filename, processed_data['title']
