FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install necessary packages
RUN apt-get update && apt-get install -y aria2

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the container
COPY bot.py .

# Expose the port Aria2 RPC uses
EXPOSE 6800

# Start the Aria2 daemon and run the bot script
CMD ["sh", "-c", "aria2c --enable-rpc --rpc-listen-all --rpc-allow-origin-all --rpc-secret=mysecret & python bot.py"]
