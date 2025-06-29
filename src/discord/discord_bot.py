import discord
from discord import app_commands
import os
from discord.ext import tasks
from datetime import time
import pytz
from services.daily_briefing import generate_briefing
from services.scrape.scrape_links import scrape
from utils.detect_link_type import detect_scraper_type
import re
import logging
from services.persist.persist_to_db import persist_to_db
from database.pg_database import get_recent_entries
from services.llm.summarizer import summarize_entries

# --- Constants ---
BRIEFING_TIME = time(hour=18, minute=30, tzinfo=pytz.utc)
BRIEFING_CHANNEL_ID = 1377194701551173662

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyClient(intents=intents)

def extract_urls(text: str) -> list[str]:
    return re.findall(r'https?://[^\s]+', text)

@tasks.loop(time=BRIEFING_TIME)
async def send_daily_briefing():
    """Sends the daily briefing to the specified channel."""
    channel = bot.get_channel(BRIEFING_CHANNEL_ID)
    if channel:
        briefing = generate_briefing()
        await channel.send(briefing)
    else:
        logger.error(f"Could not find channel with ID {BRIEFING_CHANNEL_ID}")

@bot.event
async def on_ready():
    logger.info(f"Bot logged in as {bot.user}")
    send_daily_briefing.start()

@bot.tree.command(name="brief", description="Get a real-time summary of the latest knowledge.")
async def brief(interaction: discord.Interaction):
    """Generates an on-demand summary of recent entries."""
    logger.info(f"Brief command invoked by {interaction.user.name} ({interaction.user.id})")
    await interaction.response.defer(ephemeral=True)
    try:
        logger.info("Fetching recent entries for brief command...")
        entries = get_recent_entries(limit=10)
        logger.info(f"Fetched {len(entries)} entries for brief command.")
        if not entries:
            await interaction.followup.send("No new knowledge captured in the last 24 hours.")
            logger.info("No entries found for brief command.")
            return

        logger.info("Summarizing entries for brief command...")
        summary = summarize_entries(entries)
        logger.info("Summary generated for brief command. Sending response.")
        await interaction.followup.send(f"**Here's a quick summary of what I've learned recently:**\n\n{summary}")
    except Exception as e:
        logger.error(f"Error generating brief: {str(e)}", exc_info=True)
        await interaction.followup.send("❌ An error occurred while generating the summary.")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    urls = extract_urls(message.content)

    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith("image/"):
            urls.append(attachment.url)

    if not urls:
        await message.channel.send("Please provide at least one link or image.")
        return

    for url in urls:
        try:
            logger.info(f"Processing URL: {url}")
            scraper_type = detect_scraper_type(url)
            logger.info(f"Detected scraper type: {scraper_type}")
            
            data = scrape(scraper_type, url)
            logger.info(f"Successfully scraped data from {url}")

            # Persist to DB and send result message
            persist_result = persist_to_db(data)
            await message.channel.send(f"Persistence: {persist_result}")

            embed = discord.Embed(
                title=data.title or f"{scraper_type.capitalize()} content",
                description=(data.summary if data.summary else (data.content[:1000] + ("..." if data.content and len(data.content) > 1000 else "")) if data.content else "No description."),
                url=data.url,
                color=0x3DFFCE
            )

            embed.set_footer(text=data.metadata.get("source", "Unknown source"))

            if scraper_type == "image":
                embed.set_image(url=data.url)

            await message.channel.send(embed=embed)

        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}", exc_info=True)
            await message.channel.send(
                f"❌ Failed to process `{url}`\n```{str(e)}```"
            )

def run_discord_bot():
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in .env")
        print("❌ Set DISCORD_TOKEN in your .env")
    else:
        logger.info("Starting Discord bot...")
        bot.run(token)
