# vinyl.py
import os
import discord
import yt_dlp
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

FFMPEG_OPTIONS = {
    'options': '-vn',
}

# Suppress unnecessary bug reports
yt_dlp.utils.bug_reports_message = lambda: ''

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
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else cls.ytdl.prepare_filename(data)
        return filename, data['title']

# Bot class for commands
class Vinyl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', aliases=['j'], help='Ask Vinyl to join the voice channel')
    async def _join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await ctx.message.add_reaction('☑️')
        await channel.connect()
        
    @commands.command(name='leave', aliases=['l'], help='Make Vinyl leave the voice channel')
    async def _leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client is not None:
            await voice_client.disconnect()
            await ctx.message.add_reaction('☑️')
        else:
            await ctx.send("Vinyl is not connected to a voice channel")

    @commands.command(name='play', aliases=['p'], help="Play audio from YouTube")
    async def _play(self, ctx, url):
        #try:
        server = ctx.message.guild
        voice_client = server.voice_client

        async with ctx.typing():
            file, title = await AudioSource.from_url(url, loop=bot.loop)
            voice_client.play(discord.FFmpegPCMAudio(source=file, **FFMPEG_OPTIONS))
        
        await ctx.message.add_reaction('▶️')
        await ctx.send('**Now Playing:** {}'.format(title))
        os.remove(file)
    
        #except:
            #await ctx.send("Vinyl is not connected to a voice channel currently")


    @commands.command(name='pause', help='Pause any song Vinyl is currently playing')
    async def _pause(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if voice_client is None:
            await ctx.sent("Vinyl is not connected to a voice channel currently")
        elif voice_client.is_playing():
            voice_client.pause()
            await ctx.message.add_reaction('⏸️')
        else:
            await ctx.send("Vinyl isn't playing anything")

    @commands.command(name='resume', help='Resume a paused song')
    async def _resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        
        if voice_client is None:
            await ctx.sent("Vinyl is not connected to a voice channel currently")
        elif voice_client.is_paused():
            voice_client.resume()
            await ctx.message.add_reaction('▶️')
        else:
            await ctx.send("Vinyl isn't paused currently")

    @commands.command(name='stop', aliases=['s'], help='Stop any song Vinyl is currently playing')
    async def _stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        
        if voice_client is None:
            await ctx.sent("Vinyl is not connected to a voice channel currently")
        elif voice_client.is_playing():
            voice_client.stop()
            await ctx.message.add_reaction('⏹️')
        else:
            await ctx.send("Vinyl isn't playing anything")

# Set discord intents to all for now
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='-', intents=intents)
bot.add_cog(Vinyl(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.run(TOKEN)