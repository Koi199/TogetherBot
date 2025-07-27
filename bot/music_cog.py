import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
import logging
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

# YouTube-DL options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]
        
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}
        self.current_players = {}
        
    def get_queue(self, guild_id):
        """Get or create music queue for guild"""
        if guild_id not in self.music_queues:
            self.music_queues[guild_id] = []
        return self.music_queues[guild_id]
    
    @app_commands.command(name="play", description="Play a song for you and your partner 🎵")
    @app_commands.describe(query="Song name or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        """Play music command"""
        try:
            # Check if user is in voice channel
            if not interaction.user.voice:
                await interaction.response.send_message(
                    "❌ You need to be in a voice channel to play music! Join one and try again! 💕", 
                    ephemeral=True
                )
                return
            
            voice_channel = interaction.user.voice.channel
            
            # Defer response since this might take a while
            await interaction.response.defer()
            
            # Connect to voice channel if not already connected
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if not voice_client:
                voice_client = await voice_channel.connect()
            elif voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
            
            # Search for the song
            try:
                player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
            except Exception as e:
                await interaction.followup.send(
                    f"❌ Couldn't find or play that song! Try a different search term or URL. 💔"
                )
                return
            
            guild_queue = self.get_queue(interaction.guild.id)
            
            # If nothing is playing, start immediately
            if not voice_client.is_playing():
                voice_client.play(player, after=lambda e: self.song_finished(interaction.guild.id, e))
                self.current_players[interaction.guild.id] = player
                
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{player.title}**",
                    color=0xff69b4,
                    timestamp=interaction.created_at
                )
                
                if player.thumbnail:
                    embed.set_thumbnail(url=player.thumbnail)
                
                if player.duration:
                    minutes, seconds = divmod(player.duration, 60)
                    embed.add_field(
                        name="⏱️ Duration",
                        value=f"{int(minutes):02d}:{int(seconds):02d}",
                        inline=True
                    )
                
                embed.add_field(
                    name="🎧 Requested by",
                    value=interaction.user.mention,
                    inline=True
                )
                
                embed.set_footer(text="Enjoy your music together! 💕")
                
                await interaction.followup.send(embed=embed)
            else:
                # Add to queue
                guild_queue.append({
                    'player': player,
                    'requester': interaction.user,
                    'title': player.title
                })
                
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"**{player.title}** has been added to the queue!",
                    color=0x90EE90
                )
                embed.add_field(
                    name="📍 Position",
                    value=f"{len(guild_queue)} in queue",
                    inline=True
                )
                embed.add_field(
                    name="🎧 Requested by",
                    value=interaction.user.mention,
                    inline=True
                )
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in play command: {e}")
            await interaction.followup.send(
                "❌ Something went wrong while trying to play music. Please try again! 💔"
            )
    
    def song_finished(self, guild_id, error):
        """Called when a song finishes playing"""
        if error:
            logger.error(f"Player error: {error}")
        
        # Play next song in queue
        queue = self.get_queue(guild_id)
        if queue:
            next_song = queue.pop(0)
            guild = self.bot.get_guild(guild_id)
            voice_client = discord.utils.get(self.bot.voice_clients, guild=guild)
            
            if voice_client:
                voice_client.play(
                    next_song['player'], 
                    after=lambda e: self.song_finished(guild_id, e)
                )
                self.current_players[guild_id] = next_song['player']
    
    @app_commands.command(name="stop", description="Stop music and clear the queue 🛑")
    async def stop(self, interaction: discord.Interaction):
        """Stop music command"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            self.music_queues[interaction.guild.id] = []
            
            embed = discord.Embed(
                title="🛑 Music Stopped",
                description="Music has been stopped and queue cleared!",
                color=0xff4444
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ No music is currently playing!", 
                ephemeral=True
            )
    
    @app_commands.command(name="pause", description="Pause the current song ⏸️")
    async def pause(self, interaction: discord.Interaction):
        """Pause music command"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            embed = discord.Embed(
                title="⏸️ Music Paused",
                description="Music has been paused. Use `/resume` to continue!",
                color=0xffa500
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ No music is currently playing!", 
                ephemeral=True
            )
    
    @app_commands.command(name="resume", description="Resume the paused song ▶️")
    async def resume(self, interaction: discord.Interaction):
        """Resume music command"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            embed = discord.Embed(
                title="▶️ Music Resumed",
                description="Music has been resumed!",
                color=0x90EE90
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ No music is currently paused!", 
                ephemeral=True
            )
    
    @app_commands.command(name="skip", description="Skip to the next song ⏭️")
    async def skip(self, interaction: discord.Interaction):
        """Skip song command"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # This will trigger the next song
            embed = discord.Embed(
                title="⏭️ Song Skipped",
                description="Skipped to the next song!",
                color=0x90EE90
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ No music is currently playing!", 
                ephemeral=True
            )
    
    @app_commands.command(name="queue", description="View the music queue 📝")
    async def queue(self, interaction: discord.Interaction):
        """Show music queue"""
        queue = self.get_queue(interaction.guild.id)
        current_player = self.current_players.get(interaction.guild.id)
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=0xff69b4,
            timestamp=interaction.created_at
        )
        
        if current_player:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{current_player.title}**",
                inline=False
            )
        
        if queue:
            queue_text = ""
            for i, song in enumerate(queue[:10], 1):
                queue_text += f"{i}. **{song['title']}** - {song['requester'].mention}\n"
            
            embed.add_field(
                name="📝 Up Next",
                value=queue_text,
                inline=False
            )
            
            if len(queue) > 10:
                embed.set_footer(text=f"Showing first 10 of {len(queue)} songs in queue")
        else:
            if not current_player:
                embed.description = "Queue is empty! Use `/play` to add some music! 🎶"
            else:
                embed.add_field(
                    name="📝 Up Next",
                    value="Queue is empty",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leave", description="Make the bot leave the voice channel 👋")
    async def leave(self, interaction: discord.Interaction):
        """Leave voice channel command"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        
        if voice_client:
            await voice_client.disconnect()
            self.music_queues[interaction.guild.id] = []
            if interaction.guild.id in self.current_players:
                del self.current_players[interaction.guild.id]
            
            embed = discord.Embed(
                title="👋 Left Voice Channel",
                description="See you later lovebirds! 💕",
                color=0xff69b4
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ I'm not in a voice channel!", 
                ephemeral=True
            )
