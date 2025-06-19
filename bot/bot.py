#!/usr/bin/env python3
# run_bot.py - Main entry point for the Discord bot

import os
import sys
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root to Python path to enable absolute imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Now we can use absolute imports
from scrapers.multi_source import JobScraper
from data.db import get_jobs_collection
from bot.commands import setup_commands

# Load environment variables
load_dotenv(dotenv_path="config/.env")
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "1358570300077248636"))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

async def fetch_and_post_new_jobs():
    """Fetch new jobs from all sources and post to Discord"""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Error: Could not find channel with ID {CHANNEL_ID}")
        return
        
    collection = get_jobs_collection()
    
    try:
        # Initialize the job scraper
        scraper = JobScraper()
        
        # Fetch jobs from all sources (last 14 days)
        print("Fetching jobs from all sources...")
        all_jobs = scraper.fetch_all_jobs(days=14)
        
        posted_count = 0
        for job in all_jobs:
            exists = collection.find_one({"url": job["url"]})
            if not exists:
                # Insert job into database
                result = collection.insert_one(job)
                job_id = result.inserted_id
                
                # Create Discord message
                msg = (
                    f"**{job['title']}**\n"
                    f"Company: **{job['company']}**\n"
                    f"Location: {job['location']}\n"
                    f"Posted: {job['date_posted'].strftime('%Y-%m-%d')}\n"
                    f"Source: {job['source']}\n"
                    f"[Apply here]({job['url']})\n"
                    "+--------------------------------------------------+" 
                )
                
                # Send to Discord
                await channel.send(msg)
                
                # Mark as posted
                collection.update_one(
                    {"_id": job_id}, 
                    {"$set": {"posted_to_discord": True}}
                )
                posted_count += 1
        
        if posted_count > 0:
            summary_msg = f"✅ Posted {posted_count} new job(s) from all sources!"
            print(summary_msg)
        else:
            print("No new jobs to post")
            
    except Exception as e:
        error_msg = f"ERROR fetching jobs: {str(e)}"
        print(error_msg)
        if channel:
            await channel.send(error_msg)

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f"Logged in as {bot.user}")
    print(f"Monitoring Discord channel ID: {CHANNEL_ID}")
    print("Monitoring job sources:")
    
    scraper = JobScraper()
    for source_name, config in scraper.sources.items():
        print(f"  - {config['source_name']}: {config['type']}")
    
    # Set up commands
    setup_commands(bot)
    
    # Schedule job fetching every hour
    scheduler.add_job(
        fetch_and_post_new_jobs, 
        'interval', 
        hours=1,
        id='job_fetcher'
    )
    scheduler.start()
    print("Scheduler started - checking for new jobs every hour")
    
    # Run initial job fetch
    await fetch_and_post_new_jobs()

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler"""
    print(f"ERROR occurred in event {event}: {args}")

def main():
    """Main function to run the bot"""
    if not TOKEN:
        print("ERROR: BOT_TOKEN not found in environment variables")
        print("Please check your config/.env file")
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