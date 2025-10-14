#!/usr/bin/env python3
"""
Quick Discord token verification script
"""
import asyncio
import discord
from dotenv import load_dotenv
import os

load_dotenv()

async def test_token():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ No DISCORD_TOKEN found in environment")
        return
    
    print(f"🔍 Testing token: {token[:20]}...")
    
    try:
        client = discord.Client(intents=discord.Intents.default())
        
        @client.event
        async def on_ready():
            print(f"✅ Token is valid! Bot logged in as: {client.user}")
            print(f"   Bot ID: {client.user.id}")
            print(f"   Bot is in {len(client.guilds)} servers")
            await client.close()
        
        await client.start(token)
        
    except discord.LoginFailure:
        print("❌ Invalid token - please get a new one from Discord Developer Portal")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_token())