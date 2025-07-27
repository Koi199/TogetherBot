import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)

class CalendarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="add_date", description="Add an important date to your couple's calendar 💕")
    @app_commands.describe(
        title="What's the occasion?",
        date="Date in YYYY-MM-DD format",
        time="Time in HH:MM format (optional)",
        description="Additional details about the date"
    )
    async def add_date(self, interaction: discord.Interaction, title: str, date: str, time: str = '', description: str = ''):
        """Add a date to the calendar"""
        try:
            # Parse date
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, date):
                await interaction.response.send_message(
                    "❌ Invalid date format! Please use YYYY-MM-DD (e.g., 2024-12-25)", 
                    ephemeral=True
                )
                return
            
            # Parse time if provided
            if time:
                time_pattern = r'^\d{1,2}:\d{2}$'
                if not re.match(time_pattern, time):
                    await interaction.response.send_message(
                        "❌ Invalid time format! Please use HH:MM (e.g., 14:30)", 
                        ephemeral=True
                    )
                    return
                datetime_str = f"{date} {time}"
                event_date = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            else:
                event_date = datetime.strptime(date, "%Y-%m-%d")
            
            # Check if date is in the future
            if event_date <= datetime.now():
                await interaction.response.send_message(
                    "❌ The date must be in the future! Let's plan ahead! 💖", 
                    ephemeral=True
                )
                return
            
            # Add to database
            event_id = await self.bot.db.add_calendar_event(
                interaction.guild.id,
                interaction.user.id,
                interaction.channel.id,
                title,
                description or "No description provided",
                event_date
            )
            
            # Create confirmation embed
            embed = discord.Embed(
                title="💕 Date Added Successfully!",
                description=f"**{title}** has been added to your couple's calendar!",
                color=0xff69b4,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📅 When",
                value=f"<t:{int(event_date.timestamp())}:F>",
                inline=False
            )
            
            if description:
                embed.add_field(
                    name="📝 Details",
                    value=description,
                    inline=False
                )
            
            embed.add_field(
                name="⏰ Reminder",
                value="You'll get a reminder 24 hours before!",
                inline=False
            )
            
            embed.set_footer(text=f"Event ID: {event_id} • Added by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError as e:
            await interaction.response.send_message(
                "❌ Invalid date or time format! Please check your input.", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error adding date: {e}")
            await interaction.response.send_message(
                "❌ Something went wrong while adding your date. Please try again!", 
                ephemeral=True
            )
    
    @app_commands.command(name="upcoming_dates", description="View your upcoming dates and events 💖")
    @app_commands.describe(days="Number of days to look ahead (default: 30)")
    async def upcoming_dates(self, interaction: discord.Interaction, days: int = 30):
        """Show upcoming dates"""
        try:
            if days < 1 or days > 365:
                await interaction.response.send_message(
                    "❌ Please specify between 1 and 365 days!", 
                    ephemeral=True
                )
                return
            
            events = await self.bot.db.get_upcoming_events(interaction.guild.id, days)
            
            if not events:
                embed = discord.Embed(
                    title="📅 No Upcoming Dates",
                    description="No dates planned yet! Use `/add_date` to add some special moments! 💕",
                    color=0xff69b4
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title="💕 Your Upcoming Dates",
                description=f"Here are your next {len(events)} planned moments together:",
                color=0xff69b4,
                timestamp=datetime.now()
            )
            
            for event in events[:10]:  # Limit to 10 events
                event_date = datetime.fromisoformat(event['event_date'].replace('Z', '+00:00')) if isinstance(event['event_date'], str) else event['event_date']
                days_until = (event_date - datetime.now()).days
                
                time_text = f"<t:{int(event_date.timestamp())}:F>"
                if days_until == 0:
                    time_text += " (Today! 🎉)"
                elif days_until == 1:
                    time_text += " (Tomorrow! ✨)"
                elif days_until <= 7:
                    time_text += f" (In {days_until} days)"
                
                embed.add_field(
                    name=f"💖 {event['title']}",
                    value=f"{time_text}\n{event['description'][:100]}{'...' if len(event['description']) > 100 else ''}",
                    inline=False
                )
            
            if len(events) > 10:
                embed.set_footer(text=f"Showing first 10 of {len(events)} events")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting upcoming dates: {e}")
            await interaction.response.send_message(
                "❌ Something went wrong while fetching your dates. Please try again!", 
                ephemeral=True
            )
    
    @app_commands.command(name="delete_date", description="Remove a date from your calendar")
    @app_commands.describe(event_id="The ID of the event to delete")
    async def delete_date(self, interaction: discord.Interaction, event_id: int):
        """Delete a date from the calendar"""
        try:
            success = await self.bot.db.delete_event(event_id, interaction.user.id)
            
            if success:
                embed = discord.Embed(
                    title="🗑️ Date Removed",
                    description="The date has been successfully removed from your calendar.",
                    color=0x90EE90
                )
            else:
                embed = discord.Embed(
                    title="❌ Cannot Remove Date",
                    description="Event not found or you don't have permission to delete it.",
                    color=0xff4444
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error deleting date: {e}")
            await interaction.response.send_message(
                "❌ Something went wrong while deleting the date. Please try again!", 
                ephemeral=True
            )
    
    @app_commands.command(name="date_night_ideas", description="Get random date night ideas! 💡")
    async def date_night_ideas(self, interaction: discord.Interaction):
        """Provide random date night ideas"""
        ideas = [
            "🍿 Movie marathon with your favorite snacks",
            "🍳 Cook a fancy dinner together",
            "🌟 Stargazing with hot chocolate",
            "🎮 Play co-op video games",
            "📚 Read the same book together",
            "🎨 Paint or draw portraits of each other",
            "🧩 Work on a puzzle together",
            "🎵 Create a playlist of 'your songs'",
            "📸 Take a photo walk around your neighborhood",
            "🧘 Try couples yoga or meditation",
            "🍰 Bake something delicious together",
            "🎭 Have a themed costume night",
            "💌 Write love letters to read in the future",
            "🏠 Redesign a room together",
            "🎪 Have an indoor picnic",
            "🎯 Try a new hobby together",
            "🌅 Watch the sunrise or sunset",
            "🎲 Play board games with silly stakes",
            "🍕 Order from a restaurant you've never tried",
            "💃 Have a dance party in your living room"
        ]
        
        import random
        selected_ideas = random.sample(ideas, 5)
        
        embed = discord.Embed(
            title="💡 Date Night Ideas for You Two!",
            description="Here are some cute ideas for your next date night:",
            color=0xff69b4,
            timestamp=datetime.now()
        )
        
        for i, idea in enumerate(selected_ideas, 1):
            embed.add_field(
                name=f"Idea #{i}",
                value=idea,
                inline=False
            )
        
        embed.set_footer(text="Run this command again for more ideas! 💕")
        
        await interaction.response.send_message(embed=embed)
