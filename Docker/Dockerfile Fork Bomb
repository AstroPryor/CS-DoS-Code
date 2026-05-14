FROM python:3.10-slim

# Install necessary packages, including psmisc (for killall)
RUN apt-get update && apt-get install -y psmisc

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir psutil

# Make your scripts executable
RUN chmod +x fork_bomb.sh

# Run all scripts concurrently (monitoring, detector, fork_bomb)
CMD ["sh", "-c", "python3 monitoring.py & python3 detector.py & ./fork_bomb.sh & wait"]
