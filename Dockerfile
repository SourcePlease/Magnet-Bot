FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y aria2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .

EXPOSE 6800

CMD ["sh", "-c", "aria2c --enable-rpc --rpc-listen-all --rpc-allow-origin-all --rpc-secret=mysecret & python bot.py"]
