FROM python:3.9-slim-buster
# This line tells Docker to use Python 3.9 on a minimal Debian-based image as the starting point

WORKDIR /app
# This line sets the working directory inside the container to /app

COPY . .
# This line copies the current directory contents into the /app directory in the container

RUN pip install --no-cache-dir -r requirements.txt
# This line installs the Python dependencies listed in requirements.txt without caching

ENV PYTHONPATH=/app
# These lines set environment variables for the command prefix and Python path, which can be used in your bot code
# These lines set environment variables for the bot token and command prefix (not currently used in your main code)

LABEL maintainer="Peter Tran"
LABEL version="1.0"
LABEL description="Dockerfile for Discord Python bot"

CMD ["python", "-m", "bot.bot"]
# This line specifies the command to run when the container starts, which is to execute bot.py using Python
