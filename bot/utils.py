import discord
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)

def parse_time_string(time_str):
    """Parse various time string formats"""
    # Common patterns
    patterns = [
        (r'^(\d{1,2}):(\d{2})$', '%H:%M'),  # HH:MM
        (r'^(\d{1,2}):(\d{2}):(\d{2})$', '%H:%M:%S'),  # HH:MM:SS
        (r'^(\d{1,2})(\d{2})$', '%H%M'),  # HHMM
    ]
    
    for pattern, format_str in patterns:
        match = re.match(pattern, time_str)
        if match:
            try:
                return datetime.strptime(time_str, format_str).time()
            except ValueError:
                continue
    
    raise ValueError(f"Invalid time format: {time_str}")

def parse_date_string(date_str):
    """Parse various date string formats"""
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
        r'^\d{2}-\d{2}-\d{4}$',  # MM-DD-YYYY
    ]
    
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y']
    
    for i, pattern in enumerate(patterns):
        if re.match(pattern, date_str):
            try:
                return datetime.strptime(date_str, formats[i]).date()
            except ValueError:
                continue
    
    raise ValueError(f"Invalid date format: {date_str}")

def create_error_embed(title, description, color=0xff4444):
    """Create a standardized error embed"""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    return embed

def create_success_embed(title, description, color=0x90EE90):
    """Create a standardized success embed"""
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    return embed

def create_info_embed(title, description, color=0xff69b4):
    """Create a standardized info embed"""
    embed = discord.Embed(
        title=f"💡 {title}",
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    return embed

def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS"""
    if seconds is None:
        return "Unknown"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def is_url(string):
    """Check if string is a valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(string) is not None

def truncate_string(text, max_length=100):
    """Truncate string to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_relative_time(target_date):
    """Get relative time string (e.g., 'in 3 days', '2 hours ago')"""
    now = datetime.now()
    if isinstance(target_date, str):
        target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
    
    diff = target_date - now
    
    if diff.days > 0:
        if diff.days == 1:
            return "tomorrow"
        else:
            return f"in {diff.days} days"
    elif diff.days < 0:
        abs_days = abs(diff.days)
        if abs_days == 1:
            return "yesterday"
        else:
            return f"{abs_days} days ago"
    else:
        # Same day
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if hours > 0:
            if diff.total_seconds() > 0:
                return f"in {hours} hour{'s' if hours != 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif minutes > 0:
            if diff.total_seconds() > 0:
                return f"in {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "now"

def validate_guild_member(interaction, user_id):
    """Validate that a user ID belongs to a guild member"""
    try:
        member = interaction.guild.get_member(user_id)
        return member is not None
    except:
        return False

def get_couple_emoji():
    """Get a random couple-themed emoji"""
    emojis = ["💕", "💖", "💗", "💝", "💘", "💞", "💓", "💌", "❤️", "🧡", "💛", "💚", "💙", "💜", "🤍", "🖤", "🤎"]
    import random
    return random.choice(emojis)
