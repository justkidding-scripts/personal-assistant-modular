#!/bin/bash
# Discord Bot Startup Script

echo "🤖 Starting Discord Personal Assistant Bot..."

# Clear any existing DISCORD_TOKEN environment variable to ensure .env file is used
unset DISCORD_TOKEN
unset DISCORD_GUILD_ID

# Start the bot
cd "$(dirname "$0")"
python discord_bot.py