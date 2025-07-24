import os
import sys
import asyncio
import discord
from discord.ext import commands

# Ensure absolute imports work
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from data.db import get_software_jobs_collection, get_engineering_jobs_collection, get_newgrad_software_jobs_collection, get_newgrad_engineering_jobs_collection
from scrapers.multi_source import JobScraper

# Define your Discord channel IDs
ENGINEER_CHANNEL_ID = 
SOFTWARE_CHANNEL_ID = 
SOFTWARE_NEWGRAD_CHANNEL_ID = 
ENGINEERING_NEWGRAD_CHANNEL_ID = 

@commands.command(name='postalljobs')
async def postalljobs(ctx):
    """Post all jobs from both databases using embeds"""
    software_collection = get_software_jobs_collection()
    engineering_collection = get_engineering_jobs_collection()
    newgrad_swe_channel = get_newgrad_software_jobs_collection()
    newgrad_eng_channel = get_newgrad_engineering_jobs_collection()

    # Combine jobs from all collections
    software_jobs = list(software_collection.find({}).sort("date_posted", 1))
    engineering_jobs = list(engineering_collection.find({}).sort("date_posted", 1))
    newgrad_software_jobs = list(newgrad_swe_channel.find({}).sort("date_posted", 1))
    newgrad_engineering_jobs = list(newgrad_eng_channel.find({}).sort("date_posted", 1))

    all_jobs = software_jobs + engineering_jobs + newgrad_software_jobs + newgrad_engineering_jobs
    all_jobs.sort(key=lambda x: x['date_posted'])

    if not all_jobs:
        # Create an embed for "no jobs found"
        embed = discord.Embed(
            title="No Jobs Found",
            description="There are currently no job postings available.",
            color=0xff6b6b
        )
        embed.set_footer(text="Try again later or check back soon!")
        await ctx.send(embed=embed)
        return

    # Send summary embed first
    summary_embed = discord.Embed(
        title="Job Posting Summary",
        description=f"Posting **{len(all_jobs)}** jobs (oldest first)",
        color=0x00d2d3,
        timestamp=datetime.now()
    )
    summary_embed.add_field(
        name="Breakdown",
        value=f"Software: {len(software_jobs)}\n"
              f"Engineering: {len(engineering_jobs)}\n"
              f"New Grad SWE: {len(newgrad_software_jobs)}\n"
              f"New Grad ENG: {len(newgrad_engineering_jobs)}",
        inline=False
    )
    summary_embed.set_footer(text="Job postings will be sent below")
    await ctx.send(embed=summary_embed)

    # Send individual job embeds
    for job in all_jobs:
        # Determine source collection for update
        collection = (engineering_collection if "JobRight-AI-Engineering" in job.get("source", "")
                     else software_collection)
        
        # Create job embed
        job_embed = create_job_embed(job)
        
        await ctx.send(embed=job_embed)
        
        # Update posted status
        collection.update_one(
            {"_id": job["_id"]},
            {"$set": {"posted_to_discord": True}}
        )

@commands.command(name='fetchnewjobs')
async def fetchnewjobs(ctx):
    """Manually fetch new jobs from all sources using embeds"""
    
    # Send initial status embed
    status_embed = discord.Embed(
        title="Fetching New Jobs",
        description="Searching for new job postings...",
        color=0xffa500
    )
    status_embed.set_footer(text="This may take a moment")
    status_msg = await ctx.send(embed=status_embed)
    
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
                    error_embed = discord.Embed(
                        title="Error",
                        description="Target channel not found",
                        color=0xff0000
                    )
                    await ctx.send(embed=error_embed)
                    continue
                
                # Send job embed to target channel
                job_embed = create_job_embed(job)
                await target_channel.send(embed=job_embed)
                
                # Update posted status
                collection.update_one(
                    {"_id": job_id},
                    {"$set": {"posted_to_discord": True}}
                )
        
        # Update status embed with results
        if new_jobs:
            result_embed = discord.Embed(
                title="Jobs Fetched Successfully",
                description=f"Found **{len(new_jobs)}** new job postings",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            result_embed.add_field(
                name="Details",
                value=f"Jobs posted to their respective channels\n"
                      f"Check the job channels for new postings",
                inline=False
            )
        else:
            result_embed = discord.Embed(
                title="No New Jobs Found",
                description="All current job postings have already been posted",
                color=0x87ceeb
            )
        
        result_embed.set_footer(text="Job fetch completed")
        await status_msg.edit(embed=result_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="Error Occurred",
            description=f"Failed to fetch jobs: {str(e)}",
            color=0xff0000
        )
        error_embed.set_footer(text="Please try again later")
        await status_msg.edit(embed=error_embed)


def setup_commands(bot):
    """Add commands to bot instance"""
    commands = [
        postalljobs,
        fetchnewjobs,
        # ... (add other command references here) ...
    ]
    for command in commands:
        bot.add_command(command)
    print("All commands registered")
