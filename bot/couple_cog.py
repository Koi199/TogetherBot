import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class CoupleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="love_meter", description="Check your love compatibility! 💖")
    @app_commands.describe(partner="Tag your partner")
    async def love_meter(self, interaction: discord.Interaction, partner: discord.Member):
        """Fun love compatibility meter"""
        if partner.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You can't check compatibility with yourself! Tag your partner! 💕", 
                ephemeral=True
            )
            return
        
        if partner.bot:
            await interaction.response.send_message(
                "❌ Bots can't be your romantic partner! Find a real human! 🤖💔", 
                ephemeral=True
            )
            return
        
        # Generate a "random" but consistent percentage based on user IDs
        combined_id = abs(interaction.user.id + partner.id)
        love_percentage = (combined_id % 41) + 60  # Range from 60-100%
        
        # Love meter bars
        filled_hearts = int(love_percentage / 10)
        empty_hearts = 10 - filled_hearts
        love_bar = "💖" * filled_hearts + "🤍" * empty_hearts
        
        # Love messages based on percentage
        if love_percentage >= 95:
            message = "Perfect match! You two are soulmates! ✨"
        elif love_percentage >= 85:
            message = "Amazing compatibility! Your love is strong! 💪"
        elif love_percentage >= 75:
            message = "Great match! You complement each other well! 🌟"
        elif love_percentage >= 65:
            message = "Good compatibility! Keep nurturing your love! 🌱"
        else:
            message = "Every relationship takes work! Communication is key! 💬"
        
        embed = discord.Embed(
            title="💖 Love Compatibility Meter",
            color=0xff69b4,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="💑 Couple",
            value=f"{interaction.user.mention} ❤️ {partner.mention}",
            inline=False
        )
        
        embed.add_field(
            name="📊 Compatibility Score",
            value=f"{love_bar}\n**{love_percentage}%**",
            inline=False
        )
        
        embed.add_field(
            name="💌 Message",
            value=message,
            inline=False
        )
        
        embed.set_footer(text="Love meters are just for fun! Real love is built through care and understanding! 💕")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="anniversary", description="Set your anniversary date! 💍")
    @app_commands.describe(
        partner="Tag your partner",
        date="Anniversary date in YYYY-MM-DD format"
    )
    async def set_anniversary(self, interaction: discord.Interaction, partner: discord.Member, date: str):
        """Set anniversary date"""
        try:
            if partner.id == interaction.user.id:
                await interaction.response.send_message(
                    "❌ You can't set an anniversary with yourself! 💕", 
                    ephemeral=True
                )
                return
            
            if partner.bot:
                await interaction.response.send_message(
                    "❌ Bots can't be your romantic partner! 🤖💔", 
                    ephemeral=True
                )
                return
            
            # Parse date
            anniversary_date = datetime.strptime(date, "%Y-%m-%d")
            
            # Check if date is not in the future (for first anniversary)
            if anniversary_date > datetime.now():
                await interaction.response.send_message(
                    "❌ Anniversary date should be in the past (when you first got together)! 💕", 
                    ephemeral=True
                )
                return
            
            # Add milestone to database
            user1_id = min(interaction.user.id, partner.id)  # Consistent ordering
            user2_id = max(interaction.user.id, partner.id)
            
            await self.bot.db.add_milestone(
                interaction.guild.id,
                user1_id,
                user2_id,
                "anniversary",
                anniversary_date,
                f"Anniversary between {interaction.user.display_name} and {partner.display_name}"
            )
            
            # Calculate time together
            time_together = datetime.now() - anniversary_date
            years = time_together.days // 365
            months = (time_together.days % 365) // 30
            days = time_together.days % 30
            
            time_text = ""
            if years > 0:
                time_text += f"{years} year{'s' if years != 1 else ''}, "
            if months > 0:
                time_text += f"{months} month{'s' if months != 1 else ''}, "
            time_text += f"{days} day{'s' if days != 1 else ''}"
            
            embed = discord.Embed(
                title="💍 Anniversary Set!",
                description=f"Anniversary date has been set for {interaction.user.mention} and {partner.mention}!",
                color=0xff69b4,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📅 Anniversary Date",
                value=f"<t:{int(anniversary_date.timestamp())}:D>",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Time Together",
                value=time_text,
                inline=False
            )
            
            # Calculate next anniversary
            next_anniversary = anniversary_date.replace(year=datetime.now().year)
            if next_anniversary < datetime.now():
                next_anniversary = next_anniversary.replace(year=datetime.now().year + 1)
            
            embed.add_field(
                name="🎉 Next Anniversary",
                value=f"<t:{int(next_anniversary.timestamp())}:R>",
                inline=False
            )
            
            embed.set_footer(text="Congratulations on your love! 💕")
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date format! Please use YYYY-MM-DD (e.g., 2022-02-14)", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error setting anniversary: {e}")
            await interaction.response.send_message(
                "❌ Something went wrong while setting your anniversary. Please try again!", 
                ephemeral=True
            )
    
    @app_commands.command(name="milestones", description="View your relationship milestones! 🏆")
    async def milestones(self, interaction: discord.Interaction):
        """View relationship milestones"""
        try:
            milestones = await self.bot.db.get_milestones(interaction.guild.id)
            
            if not milestones:
                embed = discord.Embed(
                    title="🏆 No Milestones Yet",
                    description="No milestones recorded yet! Use `/anniversary` to set your first milestone! 💕",
                    color=0xff69b4
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏆 Relationship Milestones",
                description="Here are your recorded milestones:",
                color=0xff69b4,
                timestamp=datetime.now()
            )
            
            for milestone in milestones[:10]:  # Limit to 10
                milestone_date = datetime.fromisoformat(milestone['milestone_date'].replace('Z', '+00:00')) if isinstance(milestone['milestone_date'], str) else milestone['milestone_date']
                user1 = interaction.guild.get_member(milestone['user1_id'])
                user2 = interaction.guild.get_member(milestone['user2_id'])
                
                user1_name = user1.display_name if user1 else "Unknown User"
                user2_name = user2.display_name if user2 else "Unknown User"
                
                embed.add_field(
                    name=f"💖 {milestone['milestone_type'].title()}",
                    value=f"**{user1_name}** & **{user2_name}**\n<t:{int(milestone_date.timestamp())}:D>\n{milestone['description'][:100]}{'...' if len(milestone['description']) > 100 else ''}",
                    inline=False
                )
            
            if len(milestones) > 10:
                embed.set_footer(text=f"Showing first 10 of {len(milestones)} milestones")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting milestones: {e}")
            await interaction.response.send_message(
                "❌ Something went wrong while fetching milestones. Please try again!", 
                ephemeral=True
            )
    
    @app_commands.command(name="love_quote", description="Get a romantic quote! 💌")
    async def love_quote(self, interaction: discord.Interaction):
        """Send a random love quote"""
        quotes = [
            "\"Love is not about how many days, months, or years you have been together. Love is about how much you love each other every single day.\" - Unknown",
            "\"Being deeply loved by someone gives you strength, while loving someone deeply gives you courage.\" - Lao Tzu",
            "\"The best thing to hold onto in life is each other.\" - Audrey Hepburn",
            "\"You know you're in love when you can't fall asleep because reality is finally better than your dreams.\" - Dr. Seuss",
            "\"Love is composed of a single soul inhabiting two bodies.\" - Aristotle",
            "\"In all the world, there is no heart for me like yours. In all the world, there is no love for you like mine.\" - Maya Angelou",
            "\"Love doesn't make the world go 'round. Love is what makes the ride worthwhile.\" - Franklin P. Jones",
            "\"True love stories never have endings.\" - Richard Bach",
            "\"The greatest happiness of life is the conviction that we are loved; loved for ourselves, or rather, loved in spite of ourselves.\" - Victor Hugo",
            "\"Love is when the other person's happiness is more important than your own.\" - H. Jackson Brown Jr.",
            "\"Two souls with but a single thought, two hearts that beat as one.\" - John Keats",
            "\"Love recognizes no barriers. It jumps hurdles, leaps fences, penetrates walls to arrive at its destination full of hope.\" - Maya Angelou",
            "\"The best love is the kind that awakens the soul and makes us reach for more.\" - Nicholas Sparks",
            "\"Love is friendship that has caught fire.\" - Ann Landers",
            "\"Where there is love there is life.\" - Mahatma Gandhi"
        ]
        
        quote = random.choice(quotes)
        
        embed = discord.Embed(
            title="💌 Love Quote for You",
            description=quote,
            color=0xff69b4,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="Spreading love, one quote at a time! 💕")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="couple_game", description="Play a fun game together! 🎮")
    async def couple_game(self, interaction: discord.Interaction):
        """Fun couple game with questions"""
        questions = [
            "What's your partner's favorite color?",
            "Where was your first date?",
            "What's your partner's biggest fear?",
            "What's your partner's dream vacation destination?",
            "What's your partner's favorite movie?",
            "What makes your partner laugh the most?",
            "What's your partner's hidden talent?",
            "What's your partner's favorite food?",
            "What's your partner's biggest goal in life?",
            "What's your partner's favorite memory of you two together?",
            "What's something your partner is really proud of?",
            "What's your partner's love language?",
            "What's your partner's favorite way to spend a weekend?",
            "What's something that always cheers up your partner?",
            "What's your partner's biggest pet peeve?"
        ]
        
        question = random.choice(questions)
        
        embed = discord.Embed(
            title="🎮 Couple's Game!",
            description=f"Here's a question for you two to discuss:\n\n**{question}**",
            color=0xff69b4,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🎯 How to Play",
            value="Take turns answering about each other and see how well you know your partner!",
            inline=False
        )
        
        embed.set_footer(text="Use this command again for a new question! 💕")
        
        await interaction.response.send_message(embed=embed)
