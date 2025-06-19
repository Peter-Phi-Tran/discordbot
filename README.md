# discordbot

Currently this is just keeping track of SWE/CS related job postings, and is ran locally LOL 

Future plans:
    - Have it run on a server or someway to not need it run locally 24/7
    - Expand to New Grad Postings
    - Expand to other Engineering postings and even roles within Business and etc

Just scraping other github repos
Ran on Windows PS but can use Venv
When cloning add .env to config/ folder with correct values for BOT_TOKEN, MONGO_URI, and CHANNEL_ID.


Build the Docker image:
docker-compose build

Start the application:
docker-compose up

If you want to run in the background (detached mode):
docker-compose up -d

To stop application:
docker-compose down

To view logs:
docker-compose logs -f

If you need to rebuild after changes:
docker-compose up --build



## --- Personal Notes ---

### Dockerfile:
Defines how to build your application image.
Installs dependencies and sets up the environment.

### docker-compose.yml:
Uses the image built by the Dockerfile.
Adds features like environment variables from .env and file mounts for development.
Makes it easy to start, stop, and manage your application with a single command.