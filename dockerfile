# Use an official, lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (this makes rebuilding faster)
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot's code into the container
COPY . .

# Tell Docker how to wake the bot up
# -u flag: unbuffered output (important for Docker logging)
CMD ["python", "-u", "main.py"]