import os
import time
import re
import subprocess
import aria2p
from pyrogram import Client, filters
from pyrogram.types import Message

# Your Bot Token
BOT_TOKEN = '6006802393:AAFeAWs0NhPDOc4_Bnd9RMEYjJniN05GELw'
API_ID = '15830858'  # You need to get these from my.telegram.org
API_HASH = '2c015c994c57b312708fecc8a2a0f1a6'  # You need to get these from my.telegram.org

# Function to start the Aria2 daemon
def start_aria2_daemon():
    aria2_process = subprocess.Popen(['aria2c', '--enable-rpc', '--rpc-listen-all', '--rpc-allow-origin-all', '--rpc-secret=mysecret'])
    return aria2_process

# Function to format the download progress
def format_progress(status):
    name = status.name
    progress = status.progress
    completed_length = status.completed_length
    total_length = status.total_length
    download_speed = status.download_speed
    peers = status.connections
    gid = status.gid

    return f"📥 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆 📥\n" \
           f"[{'▣' * (progress // 10)}{'▢' * (10 - progress // 10)}] {progress:.2f}%\n" \
           f"𝑁𝑎𝑚𝑒: {name}\n" \
           f"𝐶𝑜𝑚𝑝𝑙𝑒𝑡𝑒𝑑: {completed_length / (1024 ** 2):.2f} MB\n" \
           f"𝑇𝑜𝑡𝑎𝑙: {total_length / (1024 ** 3):.2f} GiB\n" \
           f"𝑆𝑝𝑒𝑒𝑑: {download_speed / (1024 ** 2):.2f} MiB/s\n" \
           f"𝐼𝑛𝑓𝑜: [ 𝑃 : {peers} ]\n" \
           f"𝐺𝐼𝐷: {gid}\n" \
           f"𝐸𝑛𝑔𝑖𝑛𝑒: Aria2"

# Function to handle incoming messages
async def handle_message(client: Client, message: Message):
    text = message.text
    magnet_links = re.findall(r'magnet:\?xt=urn:btih:[a-zA-Z0-9]*', text)
    
    for magnet_link in magnet_links:
        download = aria2.add_magnet(magnet_link)

        # Sending initial message
        await message.reply_text(f"Starting download: {download.name}")
        
        # Continuously update the download progress
        while True:
            status = aria2.get_download(download.gid)
            if status.is_complete:
                await message.reply_text(f"Download Complete: {status.name}")
                file_path = status.files[0].path
                await upload_file(client, message, file_path)
                break
            elif status.is_failed:
                await message.reply_text(f"Download Failed: {status.error_message}")
                break
            else:
                progress_message = format_progress(status)
                await message.edit_text(progress_message)
            time.sleep(5)

# Function to format the upload progress
def format_upload_progress(uploaded, total, speed):
    progress = uploaded / total * 100
    return f"📤 𝐔𝐏𝐋𝐎𝐀𝐃𝐈𝐍𝐆 📤: {progress:.2f}%\n" \
           f"[{'▣' * (int(progress) // 10)}{'▢' * (10 - int(progress) // 10)}]\n" \
           f"{uploaded / (1024 ** 2):.2f} MB of {total / (1024 ** 3):.2f} GB\n" \
           f"𝑆𝑝𝑒𝑒𝑑: {speed / (1024 ** 2):.2f} MB/sec\n"

# Function to upload the file with progress updates
async def upload_file(client: Client, message: Message, file_path: str):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    with open(file_path, 'rb') as file:
        upload_message = await message.reply_text(f"Starting upload: {file_name}")

        def progress_callback(current, total):
            speed = current / (time.time() - start_time)
            progress_message = format_upload_progress(current, total, speed)
            client.loop.create_task(upload_message.edit_text(progress_message))

        start_time = time.time()
        await client.send_document(message.chat.id, document=file, file_name=file_name, progress=progress_callback)
        await upload_message.edit_text(f"Upload Complete: {file_name}")

# Main function to start the bot
def main():
    # Start the Aria2 daemon
    aria2_process = start_aria2_daemon()
    
    # Initialize Aria2
    global aria2
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret="mysecret"
        )
    )

    app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
    
    @app.on_message(filters.text & ~filters.command)
    async def on_message(client, message):
        await handle_message(client, message)

    app.run()

    # Stop the Aria2 daemon when the bot stops
    aria2_process.terminate()

if __name__ == '__main__':
    main()
