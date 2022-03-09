# vinyl.py
import os
import discord
from discord import voice_client
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
        self.audio_players = {}

    def get_audio_player(self, ctx):
        audio_player = self.audio_players.get(ctx.guild.id)
        if not audio_player:
            audio_player = AudioController(self.bot, ctx)
            self.audio_players[ctx.guild.id] = audio_player
        
        return audio_player

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
            del self.audio_players[ctx.guild.id]
            
    @commands.command(name='play', aliases=['p'], help="Play")
    async def _play(self, ctx, *, search):
        if not ctx.audio_player.voice_client:
            await ctx.invoke(self._join)

        async with ctx.typing():

            try:
                source = await AudioSource.generate_source(ctx, search, loop=self.bot.loop)
            except:
                await ctx.send("An error occured while trying to play")
            else:
                if(ctx.audio_player.voice_client.is_playing()):
                    await ctx.send('**Queued:**  {}'.format(source.title))
                await ctx.audio_player.queue.put(source)
                

        await ctx.message.add_reaction('▶️')

    @commands.command(name='skip', aliases=['s'], help="Skip the song currently playing")
    async def _skip(self, ctx):
        voice_client = ctx.audio_player.voice_client

        if voice_client is None:
            await ctx.send("Vinyl is not connected to a voice channel currently")
        elif voice_client.is_playing():
            await ctx.message.add_reaction('⏭️')
            ctx.audio_player.skip()
        else:
            await ctx.send("Vinyl isn't playing anything")
        
    @commands.command(name='pause', help='Pause any song Vinyl is currently playing')
    async def _pause(self, ctx):
        voice_client = ctx.audio_player.voice_client

        if voice_client is None:
            await ctx.send("Vinyl is not connected to a voice channel currently")
        elif voice_client.is_playing():
            await ctx.message.add_reaction('⏸️')
            voice_client.pause()            
        else:
            await ctx.send("Vinyl isn't playing anything")

    @commands.command(name='resume', help='Resume a paused song')
    async def _resume(self, ctx):
        voice_client = ctx.audio_player.voice_client
        
        if voice_client is None:
            await ctx.sent("Vinyl is not connected to a voice channel currently")
        elif voice_client.is_paused():
            await ctx.message.add_reaction('▶️')
            voice_client.resume()
        else:
            await ctx.send("Vinyl isn't paused currently")

# Set discord intents to all for now
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='-', intents=intents)
bot.add_cog(Vinyl(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.run(TOKEN)