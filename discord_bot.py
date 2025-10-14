#!/usr/bin/env python3
import os
import discord
from discord.ext import commands
from discord import app_commands
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from assistant import Assistant
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!pa ", intents=intents)
assistant = Assistant()

# Logging setup
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOGS_DIR / "discord_bot.log"
_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
_handler.setFormatter(_formatter)
logger = logging.getLogger("assistant_bot")
logger.setLevel(logging.INFO)
logger.addHandler(_handler)
logger.propagate = False
# quiet down very chatty loggers
_dlogger = logging.getLogger("discord")
_dlogger.setLevel(logging.WARNING)
_dlogger.addHandler(_handler)
_dlogger.propagate = False

MAX_REPLY = 1800

@bot.event
async def on_ready():
    msg = f"Assistant bot online as {bot.user}"
    print(msg)
    logger.info(msg)
    # Sync application (slash) commands
    try:
        guild_id = os.getenv("DISCORD_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            await bot.tree.sync(guild=guild)
            s = f"Synced slash commands to guild {guild_id}"
            print(s)
            logger.info(s)
        else:
            await bot.tree.sync()
            s = "Synced global slash commands (may take up to an hour to propagate)"
            print(s)
            logger.info(s)
    except Exception as e:
        err = f"Slash command sync failed: {e}"
        print(err)
        logger.exception(err)

@bot.command(name="ask")
async def ask(ctx: commands.Context, *, question: str):
    res = assistant.handle(question)
    text = res.get("answer", "").strip() or "(no answer)"
    if len(text) > MAX_REPLY:
        text = text[:MAX_REPLY] + "..."
    await ctx.reply(text)

@bot.command(name="rag_add")
async def rag_add(ctx: commands.Context, *, path: str):
    res = assistant.handle(f"rag add {path}")
    text = res.get("answer", "") or "(done)"
    if len(text) > MAX_REPLY:
        text = text[:MAX_REPLY] + "..."
    await ctx.reply(text)

@bot.tree.command(name="rag_add", description="Index files from a server path (.txt/.md/.json)")
@app_commands.describe(path="Absolute or relative path on the bot host")
async def rag_add_slash(interaction: discord.Interaction, path: str):
    res = assistant.handle(f"rag add {path}")
    text = res.get("answer", "") or "(done)"
    await interaction.response.send_message(text, ephemeral=True)

@bot.command(name="rag_ask")
async def rag_ask(ctx: commands.Context, *, question: str):
    res = assistant.handle(f"rag ask {question}")
    text = res.get("answer", "") or "(no results)"
    if len(text) > MAX_REPLY:
        text = text[:MAX_REPLY] + "..."
    await ctx.reply(text)

@bot.tree.command(name="rag_ask", description="Ask a question grounded in indexed documents")
@app_commands.describe(question="Your question")
async def rag_ask_slash(interaction: discord.Interaction, question: str):
    res = assistant.handle(f"rag ask {question}")
    text = res.get("answer", "") or "(no results)"
    await interaction.response.send_message(text, ephemeral=False)

@bot.command(name="rag_status")
async def rag_status(ctx: commands.Context):
    res = assistant.handle("rag status")
    text = res.get("answer", "") or "(no status)"
    if len(text) > MAX_REPLY:
        text = text[:MAX_REPLY] + "..."
    await ctx.reply(text)

# Slash commands equivalents
@bot.tree.command(name="rag_status", description="Show RAG backend and document count")
async def rag_status_slash(interaction: discord.Interaction):
    res = assistant.handle("rag status")
    text = res.get("answer", "") or "(no status)"
    await interaction.response.send_message(text, ephemeral=True)

@bot.command(name="rag_add_attachments")
async def rag_add_attachments(ctx: commands.Context):
    attachments = ctx.message.attachments
    if not attachments:
        await ctx.reply("No attachments on this message. Attach .txt/.md/.json files and try again.")
        return
    count = 0
    skipped = []
    for a in attachments:
        fname = a.filename or "attachment"
        low = fname.lower()
        if not (low.endswith(".txt") or low.endswith(".md") or low.endswith(".json")):
            skipped.append(fname)
            continue
        try:
            data = await a.read()
            text = data.decode("utf-8", errors="ignore")
            doc_id = f"discord:{fname}"
            _ = assistant.handle(f"rag add_text {doc_id} :: {text}")
            count += 1
        except Exception:
            skipped.append(fname)
    msg = f"Indexed {count} attachment(s)."
    if skipped:
        msg += " Skipped: " + ", ".join(skipped)
    await ctx.reply(msg)

# Slash: accept up to 5 attachments
@bot.tree.command(name="rag_add_attachments", description="Index up to 5 attachments (.txt/.md/.json)")
@app_commands.describe(file1="Attachment 1", file2="Attachment 2", file3="Attachment 3", file4="Attachment 4", file5="Attachment 5")
async def rag_add_attachments_slash(
    interaction: discord.Interaction,
    file1: discord.Attachment | None = None,
    file2: discord.Attachment | None = None,
    file3: discord.Attachment | None = None,
    file4: discord.Attachment | None = None,
    file5: discord.Attachment | None = None,
):
    files = [f for f in [file1, file2, file3, file4, file5] if f is not None]
    if not files:
        await interaction.response.send_message("Attach .txt/.md/.json files in command options.", ephemeral=True)
        return
    count = 0
    skipped = []
    for a in files:
        fname = a.filename or "attachment"
        low = fname.lower()
        if not (low.endswith(".txt") or low.endswith(".md") or low.endswith(".json")):
            skipped.append(fname)
            continue
        try:
            data = await a.read()
            text = data.decode("utf-8", errors="ignore")
            doc_id = f"discord:{fname}"
            _ = assistant.handle(f"rag add_text {doc_id} :: {text}")
            count += 1
        except Exception:
            skipped.append(fname)
    msg = f"Indexed {count} attachment(s)."
    if skipped:
        msg += " Skipped: " + ", ".join(skipped)
    await interaction.response.send_message(msg, ephemeral=True)

@bot.command(name="triage")
async def triage_cmd(ctx: commands.Context, *, symptoms: str):
    res = assistant.handle(f"triage {symptoms}")
    text = res.get("answer", "") or "(no answer)"
    if len(text) > MAX_REPLY:
        text = text[:MAX_REPLY] + "..."
    await ctx.reply(text)

@bot.tree.command(name="triage", description="Create a pre-visit summary (not medical advice)")
@app_commands.describe(symptoms="comma-separated symptoms, e.g., 'chest pain, sweating'")
async def triage_slash(interaction: discord.Interaction, symptoms: str):
    res = assistant.handle(f"triage {symptoms}")
    text = res.get("answer", "") or "(no answer)"
    await interaction.response.send_message(text, ephemeral=True)

@bot.tree.command(name="rag_help", description="Show RAG usage")
async def rag_help_slash(interaction: discord.Interaction):
    text = (
        "RAG commands:\n"
        "- /rag_add path:<server-path>\n"
        "- /rag_add_attachments file1..file5 (txt/md/json)\n"
        "- /rag_ask question:<text>\n"
        "- /rag_status\n"
        "Prefix commands also available: !pa rag_add, !pa rag_add_attachments, !pa rag_ask, !pa rag_status."
    )
    await interaction.response.send_message(text, ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    try:
        logger.exception("Command error: %s in channel=%s by user=%s", getattr(ctx, 'command', None), getattr(ctx, 'channel', None), getattr(ctx, 'author', None))
    except Exception:
        pass

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# React with 📌 on a message containing attachments to index them
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    try:
        if payload.user_id == bot.user.id:
            return
    except Exception:
        pass
    if str(payload.emoji) != "📌":
        return
    # Fetch channel and message
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        channel = await bot.fetch_channel(payload.channel_id)
    try:
        message = await channel.fetch_message(payload.message_id)
    except Exception:
        return
    attachments = message.attachments
    if not attachments:
        return
    count = 0
    skipped = []
    for a in attachments:
        fname = a.filename or "attachment"
        low = fname.lower()
        if not (low.endswith(".txt") or low.endswith(".md") or low.endswith(".json")):
            skipped.append(fname)
            continue
        try:
            data = await a.read()
            text = data.decode("utf-8", errors="ignore")
            doc_id = f"discord:{fname}#m{message.id}"
            _ = assistant.handle(f"rag add_text {doc_id} :: {text}")
            count += 1
        except Exception:
            skipped.append(fname)
    try:
        await channel.send(f"Indexed {count} attachment(s) from a pinned message. Skipped: {', '.join(skipped) if skipped else 'none'}")
    except Exception:
        pass

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    # Process defined commands (ask, rag_add, rag_ask, rag_status, triage)
    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Set DISCORD_TOKEN in your environment.")
        raise SystemExit(1)
    bot.run(token)
