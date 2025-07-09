#!/usr/bin/env python3
import os
import sys
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.embed_utils import create_job_embed, create_error_embed, create_success_embed
from datetime import datetime



# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scrapers.multi_source import JobScraper
from data.db import get_software_jobs_collection, get_engineering_jobs_collection, ensure_indexes, get_newgrad_engineering_jobs_collection, get_newgrad_software_jobs_collection
from bot.commands import setup_commands

# Load environment variables
load_dotenv(dotenv_path="config/.env")
TOKEN = os.getenv("BOT_TOKEN")
SOFTWARE_INTERN_CHANNEL_ID = int(os.getenv("SOFTWARE_INTERN_CHANNEL_ID", ""))
ENGINEER_INTERN_CHANNEL_ID = int(os.getenv("ENGINEER_INTERN_CHANNEL_ID", ""))
SOFTWARE_NEWGRAD_CHANNEL_ID = int(os.getenv("SOFTWARE_NEWGRAD_CHANNEL_ID", ""))
ENGINEERING_NEWGRAD_CHANNEL_ID = int(os.getenv("ENGINEERING_NEWGRAD_CHANNEL_ID", ""))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

async def fetch_and_post_new_jobs():
    """Fetch new jobs and post to appropriate channels using embeds"""
    software_channel = bot.get_channel(SOFTWARE_INTERN_CHANNEL_ID)
    engineer_channel = bot.get_channel(ENGINEER_INTERN_CHANNEL_ID)
    newgrad_swe_channel = bot.get_channel(SOFTWARE_NEWGRAD_CHANNEL_ID)
    newgrad_eng_channel = bot.get_channel(ENGINEERING_NEWGRAD_CHANNEL_ID)

    if not software_channel or not engineer_channel:
        print("Error: Could not find one or more channels")
        return

    posted_count = 0
    scraper = JobScraper()
    
    try:
        print("Fetching all jobs (7-day window, capped to 100)...")
        all_jobs = scraper.fetch_all_jobs(days=7)
        
        # Send a summary to the first channel if jobs are found
        if all_jobs:
            summary_embed = discord.Embed(
                title="🔄 Automated Job Update",
                description=f"Found {len(all_jobs)} jobs to process",
                color=0x3498db,
                timestamp=datetime.now()
            )
            summary_embed.set_footer(text="Jobs will be posted to appropriate channels")
            await software_channel.send(embed=summary_embed)
        
        for job in all_jobs:
            # Pick collection & channel by role_type + source
            if job["role_type"] == "New Grad":
                if "Engineering" in job["source"] or "Product" in job["source"]:
                    collection = get_newgrad_engineering_jobs_collection()
                    channel = bot.get_channel(ENGINEERING_NEWGRAD_CHANNEL_ID)
                else:
                    collection = get_newgrad_software_jobs_collection()
                    channel = bot.get_channel(SOFTWARE_NEWGRAD_CHANNEL_ID)
            else:
                if "Engineering" in job["source"] or "Product-Management" in job["source"]:
                    collection = get_engineering_jobs_collection()
                    channel = bot.get_channel(ENGINEER_INTERN_CHANNEL_ID)
                else:
                    collection = get_software_jobs_collection()
                    channel = bot.get_channel(SOFTWARE_INTERN_CHANNEL_ID)

            # Check if job already exists
            exists = collection.find_one({"url": job["url"]})
            if not exists:
                # Insert into database
                result = collection.insert_one(job)
                job_id = result.inserted_id

                # Create and send job embed
                job_embed = create_job_embed(job)
                await channel.send(embed=job_embed)

                # Update posted status
                collection.update_one(
                    {"_id": job_id},
                    {"$set": {"posted_to_discord": True}}
                )
                posted_count += 1

        if posted_count > 0:
            print(f"✅ Posted {posted_count} new job(s) with embeds")
        else:
            print("No new jobs to post")

    except Exception as e:
        error_msg = f"ERROR fetching jobs: {str(e)}"
        print(error_msg)
        
        # Send error embed to software channel
        if software_channel:
            error_embed = discord.Embed(
                title="❌ Automated Job Fetch Error",
                description=error_msg,
                color=0xff0000,
                timestamp=datetime.now()
            )
            error_embed.set_footer(text="Please check the bot logs for more details")
            await software_channel.send(embed=error_embed)


@bot.event
async def on_ready():
    """Bot startup event"""
    print(f"Logged in as {bot.user}")
    print(f"Software Channel ID: {SOFTWARE_INTERN_CHANNEL_ID}")
    print(f"Engineer Channel ID: {ENGINEER_INTERN_CHANNEL_ID}")
    print(f"Software New Grad Channel ID: {SOFTWARE_NEWGRAD_CHANNEL_ID}")
    print(f"Engineer New Grad Channel ID: {ENGINEERING_NEWGRAD_CHANNEL_ID}")
    
    # Ensure MongoDB indexes
    ensure_indexes()
    
    # Set up commands
    setup_commands(bot)
    
    # Schedule job fetching every hour
    scheduler.add_job(
        fetch_and_post_new_jobs,
        'interval',
        hours=0.5,
        id='job_fetcher'
    )
    scheduler.start()
    print("Scheduler started - checking for new jobs every hour")
    
    # Run initial job fetch
    await fetch_and_post_new_jobs()

def main():
    if not TOKEN:
        print("ERROR: BOT_TOKEN not found in environment variables")
        return

    print("🔄 Starting Discord bot...")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("ERROR: Invalid bot token")
    except Exception as e:
        print(f"ERROR starting bot: {str(e)}")

if __name__ == "__main__":
    main()