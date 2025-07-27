# Couple Bot - Discord Bot for Couples

## Overview

Couple Bot is a Discord bot designed for couples to manage their shared activities, create romantic calendars, play music together, and track their relationship milestones. The bot is built using Python with the discord.py library and uses SQLite for data persistence.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular cog-based architecture using discord.py's commands extension framework. The system is designed as a single Discord bot with multiple feature modules (cogs) that handle different aspects of couple interaction.

### Core Components:
- **Main Bot Controller**: Handles bot initialization, event management, and cog loading
- **Database Layer**: SQLite-based persistence with async operations
- **Feature Modules (Cogs)**: Modular components for different functionalities
- **Keep-Alive Service**: Flask-based web server for hosting platform compatibility

## Key Components

### 1. Bot Core (`main.py`)
- **Purpose**: Central bot controller and initialization
- **Architecture**: Uses Discord.py's commands.Bot class with custom CoupleBot extension
- **Key Features**: 
  - Slash command synchronization
  - Background task management
  - Cog loading and management
  - Database initialization

### 2. Calendar Management (`bot/calendar_cog.py`)
- **Purpose**: Manages couple's shared calendar and important dates
- **Features**: Date validation, event scheduling, reminder system
- **Data Storage**: Events stored with guild/user association for multi-server support

### 3. Music System (`bot/music_cog.py`)
- **Purpose**: Shared music listening experience
- **Architecture**: YouTube-DL integration with Discord voice channels
- **Features**: Audio streaming, playlist management, volume control
- **Dependencies**: yt-dlp for audio extraction, FFmpeg for audio processing

### 4. Couple Activities (`bot/couple_cog.py`)
- **Purpose**: Relationship-focused interactive features
- **Features**: Love compatibility meter, relationship games
- **Algorithm**: Deterministic "randomness" based on user ID combination for consistency

### 5. Database Layer (`bot/database.py`)
- **Technology**: SQLite with aiosqlite for async operations
- **Schema Design**: 
  - `calendar_events`: Event scheduling and reminders
  - `user_preferences`: Per-user/guild settings
  - `couple_milestones`: Relationship tracking data
- **Architecture Choice**: SQLite chosen for simplicity and zero-configuration deployment

### 6. Utility Functions (`bot/utils.py`)
- **Purpose**: Shared helper functions for parsing and formatting
- **Features**: Date/time parsing, error handling, embed creation

### 7. Keep-Alive Service (`keep_alive.py`)
- **Purpose**: Web server for hosting platform requirements
- **Technology**: Flask with minimal overhead
- **Architecture**: Threaded execution to avoid blocking bot operations

## Data Flow

1. **Command Reception**: Discord slash commands received through discord.py
2. **Validation**: Input validation using regex patterns and custom parsers
3. **Database Operations**: Async SQLite operations for data persistence
4. **Response Generation**: Discord embeds and messages sent back to users
5. **Background Tasks**: Scheduled reminders and maintenance tasks

## External Dependencies

### Core Dependencies:
- **discord.py**: Primary bot framework for Discord API interaction
- **aiosqlite**: Async SQLite database operations
- **yt-dlp**: YouTube audio extraction for music features
- **Flask**: Web server for keep-alive functionality

### System Dependencies:
- **FFmpeg**: Required for audio processing and streaming
- **Python 3.8+**: Async/await support and modern Python features

## Deployment Strategy

### Hosting Requirements:
- Python runtime environment
- Persistent storage for SQLite database
- Network access for Discord API and YouTube
- Optional: Web server capabilities for keep-alive endpoint

### Configuration:
- Environment variables for Discord bot token
- No complex configuration files required
- Self-initializing database schema

### Scalability Considerations:
- Single-server deployment model
- SQLite suitable for small to medium usage
- Stateful design requires persistent storage
- Can be enhanced with PostgreSQL for larger deployments

### Development Approach:
- Modular cog system allows feature-by-feature development
- Async programming model for better performance
- Error handling and logging throughout the application
- Type hints and documentation for maintainability

The bot is designed to be easily deployable on platforms like Replit, Heroku, or similar hosting services with minimal configuration requirements.