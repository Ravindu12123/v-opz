import os
import asyncio
from telethon import TelegramClient, events
from moviepy.editor import VideoFileClip
import time
from proglog import ProgressBarLogger

# Replace with your actual credentials
API_ID = 28234847
API_HASH = 'a494667c22f483263f1e7612f4f1a576'
BOT_TOKEN = '7879947375:AAFwuV4am9rCXBUxoHX5BVuxewm2TcDXrUA'

# Directory to store videos
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# List of authorized user IDs
AUTHORIZED_USERS = {123456789, 987654321,1387186514}  # Replace with actual user IDs

# Initialize the Telegram client
client = TelegramClient('video_optimizer_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dictionary to store progress for each file
progress_dict = {}


async def progress_callback(current, total, chat_id, filename, process_name,edit):
    """Update conversion/optimization progress and send periodic messages."""
    percentage = int((current / total) * 100)

    if progress_dict.get(filename, 0) + 5 <= percentage:
        progress_dict[filename] = percentage
        asyncio.run_coroutine_threadsafe(
            client.send_message(chat_id, edit.id, text=f"{process_name} progress: {percentage}%"),
            client.loop
        )

async def download_media(event, output_dir,edit):
    """Download media with progress tracking."""
    filename = None

    def download_progress(current, total):
        progress_callback(current, total, event.chat_id, "Download", "Downloading",edit)

    filename = await event.download_media(output_dir, progress_callback=download_progress)
    return filename

async def upload_media(chat_id, file_path,edit):
    """Upload media with progress tracking."""

    def upload_progress(current, total):
        progress_callback(current, total, chat_id, "Upload", "Uploading",edit)

    await client.send_file(
        chat_id,
        file_path,
        caption="Here’s your optimized video!",
        supports_streaming=True,  # Makes the video streamable
        progress_callback=upload_progress
    )

        
async def convert_to_mp4(input_path, output_path, filename,edit):
    progress={}
    progress[filename] = {"pres":"","st":""}
    progress[filename]["pres"] = "Optimizing: 0%"
    
    class MyBarLogger(ProgressBarLogger):
      def callback(self, **changes):
        for (parameter, value) in changes.items():
            progress[filename]["st"]='Parameter %s is now %s' % (parameter, value)

      async def bars_callback(self, bar, attr, value,old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        npr=f"Optimizing: {percentage:.2f}%"
        if float(percentage) % 5 == 0:
           progress[filename]["pres"]=npr
           print(progress[filename])
           await edit.edit(f'**Optimizing**\n status: {progress[filename]["st"]}\nprecentage: {progress[filename]["pres"]}')
    
    logger = MyBarLogger()
    try:
        with VideoFileClip(input_path) as video:
            video.write_videofile(
            output_path,
            codec="libx264",
            preset="ultrafast",
            audio=True,
            logger=logger
            )
        progress[filename]["st"] = "Optimized"
    except Exception as e:
        progress[filename] = f"Error: {str(e)}"
        print(f"Error optimizing {filename}: {e}")
    print("Optimization complete for:", filename)


async def optimize_video(input_path, output_path, filename,edit):
    progress={}
    progress[filename] = {"pres":"","st":""}
    progress[filename]["pres"] = "Optimizing: 0%"
    class MyBarLogger(ProgressBarLogger):
      def callback(self, **changes):
        for (parameter, value) in changes.items():
            progress[filename]["st"]='Parameter %s is now %s' % (parameter, value)
      def bars_callback(self, bar, attr, value,old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        npr=f"Optimizing: {percentage:.2f}%"
        if float(percentage) % 5 == 0:
          progress[filename]["pres"]=npr
          print(progress[filename])
          edit.edit(f'**Optimizing**\n status: {progress[filename]["st"]}\nprecentage: {progress[filename]["pres"]}')
    
    logger = MyBarLogger()
    try:
        with VideoFileClip(input_path) as video:
            video.write_videofile(
                output_path,
                bitrate="500k",
                preset="ultrafast",
                audio=True,
                logger=logger
            )
        progress[filename]["st"] = "Optimized"
    except Exception as e:
        progress[filename] = f"Error: {str(e)}"
        print(f"Error optimizing {filename}: {e}")
    print("Optimization complete for:", filename)


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id not in AUTHORIZED_USERS:
        await event.reply("Sorry, you are not authorized to use this bot.")
        return
    await event.reply("Hello! Send me a video file, and I'll optimize it for you.")

@client.on(events.NewMessage(func=lambda e: e.video))
async def handle_video(event):
    if event.sender_id not in AUTHORIZED_USERS:
        await event.reply("Sorry, you are not authorized to use this bot.")
        return

    filename = None
    output_path = None
    mp4_path = None

    try:
        #await event.reply("Downloading your video...")
        edit=await client.send_message(event.sender_id,"**Downloading...**")
        
        filename = await download_media(event, DOWNLOAD_DIR,edit)
        output_path = os.path.join(DOWNLOAD_DIR, f"optimized_{os.path.basename(filename)}")
        mp4_path = os.path.join(DOWNLOAD_DIR, f"converted_{os.path.basename(filename)}.mp4")

        if not filename.endswith(".mp4"):
            #await event.reply("Converting video to MP4 format...")
            await edit.edit("**Converting to MP4**")
            await convert_to_mp4(filename, mp4_path, event.chat_id,edit)
            input_path = mp4_path
        else:
            input_path = filename

        #await event.reply("Optimizing the video...")
        await edit.edit("**Optimizing video...**")
        await optimize_video(input_path, output_path, event.chat_id,edit)

        #await event.reply("Uploading the optimized video...")
        await edit.edit("**Uploading...**")
        await upload_media(event.chat_id, output_path,edit)

    except Exception as e:
        #await event.reply(f"Error during processing: {e}")
        await edit.edit(f"Err during process: {e}")
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)
        if mp4_path and os.path.exists(mp4_path):
            os.remove(mp4_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)
        if filename:
            progress_dict.pop(os.path.basename(filename), None)

# Start the bot
print("Bot is running...")
client.run_until_disconnected()
