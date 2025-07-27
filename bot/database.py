import sqlite3
import aiosqlite
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="couple_bot.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize the database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Calendar events table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    event_date DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reminder_sent BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # User preferences table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, user_id, preference_key)
                )
            ''')
            
            # Couple milestones table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS couple_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    milestone_type TEXT NOT NULL,
                    milestone_date DATETIME NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Music queue table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS music_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    song_title TEXT NOT NULL,
                    song_url TEXT NOT NULL,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    played BOOLEAN DEFAULT FALSE
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def add_calendar_event(self, guild_id, user_id, channel_id, title, description, event_date):
        """Add a new calendar event"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''INSERT INTO calendar_events 
                   (guild_id, user_id, channel_id, title, description, event_date)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (guild_id, user_id, channel_id, title, description, event_date)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_upcoming_events(self, guild_id, days_ahead=30):
        """Get upcoming events for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                '''SELECT * FROM calendar_events 
                   WHERE guild_id = ? AND event_date > datetime('now') 
                   AND event_date <= datetime('now', '+{} days')
                   ORDER BY event_date ASC'''.format(days_ahead),
                (guild_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_upcoming_reminders(self):
        """Get events that need reminders (24 hours before)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                '''SELECT *, event_date as reminder_date FROM calendar_events 
                   WHERE reminder_sent = FALSE 
                   AND datetime(event_date, '-1 day') <= datetime('now')
                   AND event_date > datetime('now')''',
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def mark_reminder_sent(self, event_id):
        """Mark reminder as sent"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE calendar_events SET reminder_sent = TRUE WHERE id = ?',
                (event_id,)
            )
            await db.commit()
    
    async def delete_event(self, event_id, user_id):
        """Delete an event (only by the creator)"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'DELETE FROM calendar_events WHERE id = ? AND user_id = ?',
                (event_id, user_id)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def set_user_preference(self, guild_id, user_id, key, value):
        """Set a user preference"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT OR REPLACE INTO user_preferences 
                   (guild_id, user_id, preference_key, preference_value)
                   VALUES (?, ?, ?, ?)''',
                (guild_id, user_id, key, value)
            )
            await db.commit()
    
    async def get_user_preference(self, guild_id, user_id, key, default=None):
        """Get a user preference"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''SELECT preference_value FROM user_preferences 
                   WHERE guild_id = ? AND user_id = ? AND preference_key = ?''',
                (guild_id, user_id, key)
            )
            row = await cursor.fetchone()
            return row[0] if row else default
    
    async def add_milestone(self, guild_id, user1_id, user2_id, milestone_type, milestone_date, description):
        """Add a couple milestone"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''INSERT INTO couple_milestones 
                   (guild_id, user1_id, user2_id, milestone_type, milestone_date, description)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (guild_id, user1_id, user2_id, milestone_type, milestone_date, description)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_milestones(self, guild_id):
        """Get all milestones for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                '''SELECT * FROM couple_milestones 
                   WHERE guild_id = ? ORDER BY milestone_date DESC''',
                (guild_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
