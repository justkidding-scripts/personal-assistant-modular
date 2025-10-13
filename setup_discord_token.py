#!/usr/bin/env python3
"""
Discord Bot Token Setup Script
"""
import os
import sys

def setup_discord_token():
    print("=== Discord Bot Token Setup ===")
    print()
    print("To get your Discord bot token:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Create a new application or select existing one")
    print("3. Go to the 'Bot' tab")
    print("4. Click 'Reset Token' and copy the new token")
    print("5. Make sure to enable 'Message Content Intent' in the Bot settings")
    print()
    
    token = input("Enter your Discord bot token: ").strip()
    
    if not token or token == "your_actual_bot_token_here":
        print("❌ Invalid token provided!")
        sys.exit(1)
    
    guild_id = input("Enter your Discord server ID (optional, press Enter to skip): ").strip()
    
    # Read existing .env file
    env_lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_lines = f.readlines()
    
    # Update or add token
    updated = False
    for i, line in enumerate(env_lines):
        if line.startswith("DISCORD_TOKEN="):
            env_lines[i] = f"DISCORD_TOKEN={token}\n"
            updated = True
            break
    
    if not updated:
        env_lines.append(f"DISCORD_TOKEN={token}\n")
    
    # Update or add guild ID if provided
    if guild_id:
        guild_updated = False
        for i, line in enumerate(env_lines):
            if line.startswith("DISCORD_GUILD_ID="):
                env_lines[i] = f"DISCORD_GUILD_ID={guild_id}\n"
                guild_updated = True
                break
        
        if not guild_updated:
            env_lines.append(f"DISCORD_GUILD_ID={guild_id}\n")
    
    # Write back to .env
    with open(".env", "w") as f:
        f.writelines(env_lines)
    
    print()
    print("✅ Discord bot token configured successfully!")
    print("You can now run: python discord_bot.py")
    print()
    print("Don't forget to:")
    print("- Invite your bot to your Discord server")
    print("- Enable 'Message Content Intent' in bot settings")
    print("- Give the bot necessary permissions (Send Messages, Use Slash Commands, etc.)")

if __name__ == "__main__":
    setup_discord_token()