import discord
from datetime import datetime

def create_job_embed(job):
    """
    Create a professional embed for job postings with improved formatting.
    Args:
        job (dict): Job data containing title, company, location, etc.
    Returns:
        discord.Embed: Formatted embed ready to send
    """
    # Choose colors based on job type
    color_mapping = {
        'New Grad': 0x00ff7f,      # Spring Green
        'Internship': 0x1e90ff     # Dodger Blue
    }
    embed_color = color_mapping.get(job.get('role_type', 'Internship'), 0x1e90ff)

    # Format the date
    if isinstance(job['date_posted'], datetime):
        formatted_date = job['date_posted'].strftime('%B %d, %Y')
    else:
        formatted_date = datetime.fromtimestamp(job['date_posted']).strftime('%B %d, %Y')

    # Create the main embed
    embed = discord.Embed(
        title=f"{job.get('emoji', '')} {job['title']}".strip(),
        color=embed_color,
        timestamp=datetime.now()
    )

    # Add thumbnail if provided
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1387856625364238508/1392205237363933244/Vertical_version.png?ex=686eafaa&is=686d5e2a&hm=55a56c825ba02837b34fb5d7eaf91729866858e9edf63e77b370b6cec0967714&")

    # Add fields for better spacing and alignment
    embed.add_field(name="Company", value=job['company'], inline=False)
    embed.add_field(name="Location", value=job['location'] or 'Remote/Not specified', inline=False)
    embed.add_field(name="Posted", value=formatted_date, inline=False) 

    # Add a field for the apply link (not inline to keep it prominent)
    embed.add_field(name="\u200B", value=f"[Apply Here]({job['url']})", inline=False)

    # Add footer with source information
    source_name = job.get('source', 'Unknown')
    embed.set_footer(text=f"{source_name}")

    return embed

def create_compact_job_embed(job):
    """
    Create an even more compact version for bulk posting.
    """
    color_mapping = {
        'New Grad': 0x00ff7f,
        'Internship': 0x1e90ff
    }
    embed_color = color_mapping.get(job.get('role_type', 'Internship'), 0x1e90ff)

    # Format the date
    if isinstance(job['date_posted'], datetime):
        formatted_date = job['date_posted'].strftime('%m/%d/%Y')
    else:
        formatted_date = datetime.fromtimestamp(job['date_posted']).strftime('%m/%d/%Y')

    # Super compact format
    description = (
        f"**{job['company']}**\n"
        f"📍 {job['location'] or 'Remote'} • 📅 {formatted_date}\n"
        f"🔗 [Apply Here]({job['url']})"
    )

    embed = discord.Embed(
        title=job['title'],
        description=description,
        color=embed_color
    )

    # Minimal footer
    source_name = job.get('source', 'Unknown')
    embed.set_footer(text=f"💡 {source_name}")

    return embed

def create_error_embed(title, description, error_type="general"):
    """Create a standardized error embed"""
    colors = {
        "general": 0xff0000,
        "warning": 0xffa500,
        "info": 0x3498db,
        "success": 0x00ff00
    }
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=colors.get(error_type, 0xff0000),
        timestamp=datetime.now()
    )
    embed.set_footer(text="Please try again or contact support")
    return embed

def create_success_embed(title, description):
    """Create a standardized success embed"""
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Operation completed successfully")
    return embed
