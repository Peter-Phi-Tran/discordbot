# Discord Job Scraper Bot

A Discord bot that scrapes SWE/CS-related job postings from GitHub repositories and posts them to a designated channel. Currently run locally, with future plans for broader functionality and deployment.

---

## ✨ Features

- Tracks Software Engineering / CS internships and new grad roles  
- Posts jobs to a Discord channel via bot  
- Scrapes data from curated GitHub repositories  
- Uses MongoDB for data persistence  
- Dockerized for easier deployment  

---

## ⚙️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Peter-Phi-Tran/discordbot
cd discordbot
```

### 2. Environment Setup
Create a `.env` file inside the `config/` folder with the following variables:
```
BOT_TOKEN=your_discord_bot_token
CHANNEL_ID=your_discord_channel_id
MONGO_URI=mongodb://localhost:27017/engjobs
SCRAPE_INTERVAL_HOURS=1
DAYS_LOOKBACK=14
```

### 3. Run Locally (Optional)
```bash
# Optional: Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

---

## 🐳 Running with Docker

### Build the Docker image
```bash
docker-compose build
```

### Start the bot
```bash
docker-compose up
```

### Run in detached mode (background)
```bash
docker-compose up -d
```

### Stop the bot
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Rebuild after changes
```bash
docker-compose up --build
```

---

## 🧠 Future Plans

- Host on a server or cloud platform to avoid running locally
- Expand to include:
  - New Grad postings
  - Other engineering disciplines (e.g., ME, EE)
  - Roles outside of engineering (e.g., Business, Design, Marketing)
- Build a web dashboard to manage sources, filters, and output

---

## 📁 Personal Notes

### `Dockerfile`
Defines how to build the application container:
- Installs dependencies
- Sets up the Python environment
- Runs the bot

### `docker-compose.yml`
Simplifies running the application:
- Loads environment variables from `.env`
- Mounts code for development
- Manages services with simple commands

---

## 📝 Notes

- Was ran on Windows PowerShell
- Compatible with Python virtual environments
- Requires `.env` setup in `config/` folder to run correctly
