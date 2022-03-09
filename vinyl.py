# vinyl.py
import os
import discord
from audio_source import AudioSource
from audio_controller import AudioController
import yt_dlp
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Suppress unnecessary bug reports
yt_dlp.utils.bug_reports_message = lambda: ''

# Bot class for commands
class Vinyl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_audio_player(self, ctx):
        return AudioController(self.bot, ctx)

    async def cog_before_invoke(self, ctx):
        ctx.audio_player = self.get_audio_player(ctx)

    async def cog_command_error(self, ctx, error):
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', aliases=['j'], help='Ask Vinyl to join your voice channel')
    async def _join(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel and not ctx.author.voice.channel:
            await ctx.send("{} is not connected to a voice channel".format(ctx.author.name))
            return
        
        channel = channel or ctx.author.voice.channel
        if ctx.audio_player.voice_client:
            await ctx.audio_player.voice_client.move_to(channel)
            return

        await ctx.message.add_reaction('☑️')
        ctx.audio_player.voice_client = await channel.connect()
        
    @commands.command(name='leave', aliases=['l'], help='Make Vinyl leave your voice channel')
    async def _leave(self, ctx):
        if not ctx.audio_player.voice_client:
            await ctx.send("Vinyl is not connected to a voice channel")
        else:
            await ctx.message.add_reaction('☑️')
            await ctx.audio_player.stop()
            

    @commands.command(name='play', aliases=['p'], help="Play")
    async def _play(self, ctx, *, search):
        #try:
        server = ctx.message.guild
        voice_client = server.voice_client

        async with ctx.typing():
            source, title = await AudioSource.generate_source(ctx, search, loop=bot.loop)
            voice_client.play(source)
        
        await ctx.message.add_reaction('▶️')
        await ctx.send('**Now Playing:** {}'.format(title))
        #except:
           #await ctx.send("An error occured while trying to play")


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