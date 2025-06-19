# bot/commands.py

import os
import sys
from discord.ext import commands
import asyncio

# Ensure absolute imports work
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.db import get_jobs_collection
from scrapers.multi_source import JobScraper

@commands.command(name='postalljobs')
async def postalljobs(ctx):
    """Post all jobs from the database to Discord (oldest first)"""
    collection = get_jobs_collection()
    # Sort by date_posted in ascending order (oldest first)
    jobs = list(collection.find({}).sort("date_posted", 1))
    
    if not jobs:
        await ctx.send("📭 No jobs found in the database.")
        return
    
    await ctx.send(f"📋 Posting {len(jobs)} jobs from database (oldest first)...")
    
    for job in jobs:
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
    """Manually trigger job fetching from all sources"""
    await ctx.send("🔍 Fetching new jobs from all sources...")
    
    collection = get_jobs_collection()
    scraper = JobScraper()
    
    try:
        # Fetch jobs from all sources
        all_jobs = scraper.fetch_all_jobs(days=14)
        
        new_jobs_count = 0
        for job in all_jobs:
            exists = collection.find_one({"url": job["url"]})
            if not exists:
                # Insert into database
                result = collection.insert_one(job)
                job_id = result.inserted_id
                
                # Post to Discord
                msg = (
                    f"**{job['title']}**\n"
                    f"Company: **{job['company']}**\n"
                    f"Location: {job['location']}\n"
                    f"Posted: {job['date_posted'].strftime('%Y-%m-%d')}\n"
                    f"Source: {job['source']}\n"
                    f"[Apply here]({job['url']})\n"
                    "+--------------------------------------------------+" 
                ) 
                await ctx.send(msg)
                
                # Mark as posted
                collection.update_one(
                    {"_id": job_id}, 
                    {"$set": {"posted_to_discord": True}}
                )
                new_jobs_count += 1
            
    except Exception as e:
        await ctx.send(f"❌ Error fetching jobs: {str(e)}")

@commands.command(name='sources')
async def sources(ctx):
    """List all configured job sources"""
    scraper = JobScraper()
    source_list = "📊 **Configured Job Sources:**\n\n"
    
    for i, (source_key, config) in enumerate(scraper.sources.items(), 1):
        source_list += f"{i}. **{config['source_name']}**\n"
        source_list += f"   Type: {config['type']}\n"
        source_list += f"   URL: {config['url'][:50]}...\n\n"
    
    await ctx.send(source_list)

@commands.command(name='jobstats')
async def jobstats(ctx):
    """Show database statistics"""
    collection = get_jobs_collection()
    
    total_jobs = collection.count_documents({})
    posted_jobs = collection.count_documents({"posted_to_discord": True})
    unposted_jobs = total_jobs - posted_jobs
    
    # Get jobs by source
    pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    source_stats = list(collection.aggregate(pipeline))
    
    stats_msg = f"📊 **Job Database Statistics:**\n\n"
    stats_msg += f"📋 Total Jobs: {total_jobs}\n"
    stats_msg += f"✅ Posted to Discord: {posted_jobs}\n"
    stats_msg += f"⏳ Not Posted: {unposted_jobs}\n\n"
    stats_msg += f"**Jobs by Source:**\n"
    
    for stat in source_stats:
        source_name = stat['_id'] or 'Unknown'
        count = stat['count']
        stats_msg += f"• {source_name}: {count}\n"
    
    await ctx.send(stats_msg)

@commands.command(name='postjobsbysource')
async def postjobsbysource(ctx, source_name_or_index: str):
    """
    Post all jobs from a specified source (by name or index) - oldest first.
    Usage: !postjobsbysource <source_name_or_index>
    Example: !postjobsbysource JobRight-AI   or   !postjobsbysource 3
    """
    collection = get_jobs_collection()
    scraper = JobScraper()

    #Try to interpret as index
    try:
        index = int(source_name_or_index) - 1
        source_keys = list(scraper.sources.keys())
        if 0 <= index < len(source_keys):
            source_key = source_keys[index]
            source_name = scraper.sources[source_key]['source_name']
        else:
            await ctx.send("❌ Invalid source index. Please provide a valid index.")
            return
    except ValueError:
        # Not an index, treat as name
        source_name = source_name_or_index.strip()
        source_key = None
        for k, v in scraper.sources.items():
            if v['source_name'].lower() == source_name.lower():
                source_key = k
                break
        if not source_key:
            await ctx.send(f"❌ Source not found: {source_name_or_index}. Use `!postsources` to see available sources.")
            return

    # Sort by date_posted in ascending order (oldest first)
    jobs = list(collection.find({"source": source_name}).sort("date_posted", 1))
    if not jobs:
        await ctx.send(f"📭 No jobs found for source: {source_name}")
        return

    await ctx.send(f"📋 Posting all jobs from source: **{source_name}** ({len(jobs)} jobs, oldest first)...")

    for job in jobs:
        msg = (
            f"**{job['title']}**\n"
            f"Company: **{job['company']}**\n"
            f"Location: {job['location']}\n"
            f"Posted: {job['date_posted'].strftime('%Y-%m-%d')}\n"
            f"Source: {job['source']}\n"
            f"[Apply here]({job['url']})\n"
            "+--------------------------------------------------+"
        )
        await ctx.send(msg)
        collection.update_one(
            {"_id": job["_id"]},
            {"$set": {"posted_to_discord": True}}
        )

@commands.command(name='postsources')
async def postsources(ctx):
    """
    List all available job sources (by name and index).
    Usage: !postsources
    """
    scraper = JobScraper()
    source_list = "📊 **Available Job Sources:**\n\n"
    for i, (source_key, config) in enumerate(scraper.sources.items(), 1):
        source_list += f"{i}. **{config['source_name']}**\n"
        source_list += f"   Type: {config['type']}\n"
        source_list += f"   URL: {config['url'][:50]}...\n\n"
    await ctx.send(source_list)


@commands.command(name='postjobsbysource_index')
async def postjobsbysource_index(ctx, index: int):
    """
    Post all jobs from a specified source by its index (oldest first).
    Usage: !postjobsbysource_index <index>
    Example: !postjobsbysource_index 3
    """
    collection = get_jobs_collection()
    scraper = JobScraper()
    source_keys = list(scraper.sources.keys())
    if index < 1 or index > len(source_keys):
        await ctx.send(f"❌ Invalid source index. Use `!postsources` to see available sources.")
        return
    source_key = source_keys[index - 1]
    source_name = scraper.sources[source_key]['source_name']
    
    # Sort by date_posted in ascending order (oldest first)
    jobs = list(collection.find({"source": source_name}).sort("date_posted", 1))
    if not jobs:
        await ctx.send(f"📭 No jobs found for source: {source_name}")
        return

    await ctx.send(f"📋 Posting all jobs from source: **{source_name}** ({len(jobs)} jobs, oldest first)...")

    for job in jobs:
        msg = (
            f"**{job['title']}**\n"
            f"Company: **{job['company']}**\n"
            f"Location: {job['location']}\n"
            f"Posted: {job['date_posted'].strftime('%Y-%m-%d')}\n"
            f"Source: {job['source']}\n"
            f"[Apply here]({job['url']})\n"
            "+--------------------------------------------------+"
        )
        await ctx.send(msg)
        collection.update_one(
            {"_id": job["_id"]},
            {"$set": {"posted_to_discord": True}}
        )

@commands.command(name='cleardb')
async def cleardb(ctx):
    """Clear all jobs from the database - USE WITH CAUTION!"""
    collection = get_jobs_collection()
    
    count_before = collection.count_documents({})
    await ctx.send(f"⚠️ About to delete {count_before} jobs from database. React with ✅ to confirm.")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅'
    
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        # Delete all documents
        result = collection.delete_many({})
        await ctx.send(f"🗑️ Deleted {result.deleted_count} jobs from database")
        
    except asyncio.TimeoutError:
        await ctx.send("❌ Deletion cancelled - no confirmation received")

@commands.command(name='help_jobs')
async def help_jobs(ctx):
    """Show available job bot commands"""
    help_msg = """
🤖 **Job Bot Commands:**

`!fetchnewjobs` - Manually fetch new jobs from all sources
`!postalljobs` - Post all jobs from database to Discord (oldest first)
`!sources` - List all configured job sources
`!jobstats` - Show database statistics
`!help_jobs` - Show this help message

**Automatic Features:**
• Fetches new jobs every hour automatically
• Only posts jobs from the last 14 days
• Prevents duplicate job postings
• Tracks jobs from multiple sources
"""
    await ctx.send(help_msg)

def setup_commands(bot):
    """Add all commands to the bot instance"""
    bot.add_command(cleardb)
    bot.add_command(postalljobs)
    bot.add_command(fetchnewjobs)
    bot.add_command(sources)
    bot.add_command(jobstats)
    bot.add_command(help_jobs)
    bot.add_command(postjobsbysource)
    bot.add_command(postsources)
    bot.add_command(postjobsbysource_index)
    print("✅ All commands registered successfully")