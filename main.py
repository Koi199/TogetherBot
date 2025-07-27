import os
import discord
from discord.ext import commands, tasks
import asyncio
import logging
from bot.database import Database
from bot.calendar_cog import CalendarCog
from bot.music_cog import MusicCog
from bot.couple_cog import CoupleCog
from keep_alive import keep_alive

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
# Removed privileged intents (message_content, members) for easier setup

class CoupleBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        self.db = Database()
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        # Initialize database
        await self.db.init_db()
        
        # Add cogs
        await self.add_cog(CalendarCog(self))
        await self.add_cog(MusicCog(self))
        await self.add_cog(CoupleCog(self))
        
        # Start background tasks
        self.reminder_task.start()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="over you two lovebirds 💕"
        )
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            logger.error(f"Unexpected error: {error}")
            await ctx.send("❌ Something went wrong! Please try again later.")

    @tasks.loop(hours=1)
    async def reminder_task(self):
        """Check for upcoming reminders every hour"""
        try:
            upcoming_reminders = await self.db.get_upcoming_reminders()
            
            for reminder in upcoming_reminders:
                guild = self.get_guild(reminder['guild_id'])
                if guild:
                    channel = guild.get_channel(reminder['channel_id'])
                    if channel and hasattr(channel, 'send'):
                        embed = discord.Embed(
                            title="💕 Reminder Alert!",
                            description=f"**{reminder['title']}**\n\n{reminder['description']}",
                            color=0xff69b4,
                            timestamp=reminder['reminder_date']
                        )
                        embed.add_field(
                            name="When",
                            value=f"<t:{int(reminder['event_date'].timestamp())}:F>",
                            inline=False
                        )
                        embed.set_footer(text="Don't forget! 💖")
                        
                        await channel.send(
                            f"<@{reminder['user_id']}>",
                            embed=embed
                        )
                        
                        # Mark reminder as sent
                        await self.db.mark_reminder_sent(reminder['id'])
                        
        except Exception as e:
            logger.error(f"Error in reminder task: {e}")

    @reminder_task.before_loop
    async def before_reminder_task(self):
        """Wait until bot is ready before starting reminder task"""
        await self.wait_until_ready()

# Bot instance
bot = CoupleBot()

# Run the bot
if __name__ == "__main__":
    # Keep alive for Replit
    keep_alive()
    
    # Get token from environment
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not token:
        logger.error("No Discord bot token found! Please set DISCORD_BOT_TOKEN in Replit Secrets.")
        exit(1)
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
