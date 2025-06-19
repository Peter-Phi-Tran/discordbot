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
