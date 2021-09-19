# vinyl.py
import os
import discord
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set discord intents to all for now
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

# Suppress noise about consule usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
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

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Class to download youtube audio and return filenames
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename, data['title']

@bot.command(name='join', aliases=['j'], help='Ask Vinyl to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', aliases=['l'], help='Make Vinyl leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client is not None:
        await voice_client.disconnect()
    else:
        await ctx.send("Vinyl is not connected to a voice channel")

@bot.command(name='play', aliases=['p'], help="Play audio from YouTube")
async def play(ctx,url):
    try:
        server = ctx.message.guild
        voice_client = server.voice_client

        async with ctx.typing():
            file, title = await YTDLSource.from_url(url, loop=bot.loop)
            voice_client.play(discord.FFmpegPCMAudio(source=file))
            
        
        await ctx.send('**Now Playing:** {}'.format(title))
        os.remove(file)
    
    except:
        await ctx.send("Vinyl is not connected to a voice channel currently")

@bot.command(name='pause', help='Pause any song Vinyl is currently playing')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client

    if voice_client is None:
        await ctx.sent("Vinyl is not connected to a voice channel currently")
    elif voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("Vinyl isn't playing anything")

@bot.command(name='resume', help='Resume a paused song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    
    if voice_client is None:
        await ctx.sent("Vinyl is not connected to a voice channel currently")
    elif voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("Vinyl isn't paused currently")

@bot.command(name='stop', aliases=['s'], help='Stop any song Vinyl is currently playing')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    
    if voice_client is None:
        await ctx.sent("Vinyl is not connected to a voice channel currently")
    elif voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("Vinyl isn't playing anything")

bot.run(TOKEN)