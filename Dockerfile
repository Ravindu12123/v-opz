# Use a base Python image
FROM python:3.9-slim

# Install dependencies for ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script and other necessary files into the container
COPY . .

# Run the bot
CMD ["python", "bot.py"]
