import os
import sys
import asyncio
from discord.ext import commands

# Ensure absolute imports work
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from data.db import get_software_jobs_collection, get_engineering_jobs_collection
from scrapers.multi_source import JobScraper

# Define your Discord channel IDs
ENGINEER_CHANNEL_ID = 
SOFTWARE_CHANNEL_ID = 

@commands.command(name='postalljobs')
async def postalljobs(ctx):
    """Post all jobs from both databases (oldest first)"""
    software_collection = get_software_jobs_collection()
    engineering_collection = get_engineering_jobs_collection()
    
    # Combine jobs from both collections
    software_jobs = list(software_collection.find({}).sort("date_posted", 1))
    engineering_jobs = list(engineering_collection.find({}).sort("date_posted", 1))
    all_jobs = software_jobs + engineering_jobs
    all_jobs.sort(key=lambda x: x['date_posted'])  # Sort all by date
    
    if not all_jobs:
        await ctx.send("📭 No jobs found")
        return
        
    await ctx.send(f"📋 Posting {len(all_jobs)} jobs (oldest first):")
    for job in all_jobs:
        # Determine source collection for update
        collection = (engineering_collection if "JobRight-AI-Engineering" in job.get("source", "")
                     else software_collection)
        
        msg = (
            f"**{job['title']}**\n"
            f"Company: **{job['company']}**\n"
            f"Location: {job['location']}\n"
            f"Posted: {job['date_posted'].strftime('%Y-%m-%d')}\n"
            f"Source: {job.get('source', 'Unknown')}\n"
            f"[Apply here]({job['url']})\n"
            "+--------------------------------------------------+"
        )
        await ctx.send(msg)
        collection.update_one(
            {"_id": job["_id"]},
            {"$set": {"posted_to_discord": True}}
        )

@commands.command(name='fetchnewjobs')
async def fetchnewjobs(ctx):
    """Manually fetch new jobs from all sources"""
    await ctx.send("🔍 Fetching new jobs...")
    scraper = JobScraper()
    
    try:
        jobs = scraper.fetch_all_jobs(days=7)
        new_jobs = []
        for job in jobs:
            # Select appropriate collection
            if "JobRight-AI-Engineering" in job.get("source", ""):
                collection = get_engineering_jobs_collection()
            else:
                collection = get_software_jobs_collection()
                
            if not collection.find_one({"url": job["url"]}):
                result = collection.insert_one(job)
                job_id = result.inserted_id
                new_jobs.append(job)
                
                # Determine target channel
                if "JobRight-AI-Engineering" in job.get("source", ""):
                    target_channel = ctx.bot.get_channel(ENGINEER_CHANNEL_ID)
                else:
                    target_channel = ctx.bot.get_channel(SOFTWARE_CHANNEL_ID)
                
                if not target_channel:
                    await ctx.send("❌ Error: Target channel not found")
                    continue
                    
                msg = (
                    f"**{job['title']}**\n"
                    f"Company: **{job['company']}**\n"
                    f"Location: {job['location']}\n"
                    f"Posted: {job['date_posted'].strftime('%Y-%m-%d')}\n"
                    f"Source: {job['source']}\n"
                    f"[Apply here]({job['url']})\n"
                    "+--------------------------------------------------+"
                )
                await target_channel.send(msg)
                collection.update_one(
                    {"_id": job_id},
                    {"$set": {"posted_to_discord": True}}
                )
        await ctx.send(f"✅ Found {len(new_jobs)} new jobs")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

def setup_commands(bot):
    """Add commands to bot instance"""
    commands = [
        postalljobs,
        fetchnewjobs,
        # ... (add other command references here) ...
    ]
    for command in commands:
        bot.add_command(command)
    print("✅ All commands registered")
