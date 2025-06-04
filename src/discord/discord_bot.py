import discord
import os
from services.scrape.scrape_links import scrape
from utils.detect_link_type import detect_scraper_type
import re
import logging
from services.persist.persist_to_db import persist_to_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Client(intents=intents)

def extract_urls(text: str) -> list[str]:
    # Finds all http/https URLs in the message
    return re.findall(r'https?://[^\s]+', text)

@bot.event
async def on_ready():
    logger.info(f"Bot logged in as {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # --- NEW: Handle @Web search queries ---
    if message.content.strip().lower().startswith("@web"):
        query = message.content.strip()[4:].strip()
        if not query:
            await message.channel.send("Please provide a search query after @Web.")
            return
        try:
            from database.chroma_db import query_document
            logger.info(f"@Web search query: {query}")
            results = query_document(query_text=query, n_results=3)
            docs = results.get("documents", [[]])[0]
            if not docs or all(not doc for doc in docs):
                await message.channel.send(f"No results found for: {query}")
                return
            response = "\n\n".join(f"**Result {i+1}:**\n{doc[:1000]}{'...' if doc and len(doc) > 1000 else ''}" for i, doc in enumerate(docs) if doc)
            await message.channel.send(f"**Top results for:** `{query}`\n\n{response}")
        except Exception as e:
            logger.error(f"Error in @Web search: {str(e)}", exc_info=True)
            await message.channel.send(f"❌ Failed to search: `{query}`\n```{str(e)}```")
        return
    # --- END NEW ---

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
