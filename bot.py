import os
import time
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from dotenv import load_dotenv
from handlers.photo_handler import handle_photo
from plugins.start import start_handler
from plugins.help import help_handler
from db import mongo_db

load_dotenv()

API_ID = os.getenv('API_ID', 'your_api_id')
API_HASH = os.getenv('API_HASH', 'your_api_hash')
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token')
ADMIN_ID = int(os.getenv('ADMIN_ID', 'your_admin_id'))
LOG_GROUP_ID = -1002395548077

app = Client("my_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

health_app = Flask(__name__)

@health_app.route('/health', methods=['GET'])
def health_check():
    return "Bot is running", 200

def run_flask():
    health_app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask, daemon=True).start()

async def log_new_user(user_id, username):
    message = f"New user 😗\nId: {user_id}\nUsername: {username}\n#new_user"
    try:
        await app.send_message(LOG_GROUP_ID, message)
    except Exception as e:
        print("Error sending log message:", e)

@app.on_message(filters.photo)
async def photo_handler(client: Client, message):
    response_data = await handle_photo(client, message)
    await mongo_db.insert_upload(response_data)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"

    user_data = {
        "user_id": user_id,
        "username": username,
    }
    
    try:
        existing_user = await mongo_db.users_collection.find_one({"user_id": user_id})
        
        if existing_user is None:
            await mongo_db.insert_user(user_id)
            print("User data updated:", user_data)
            await log_new_user(user_id, username)
        else:
            print("User already exists in the database:", user_data)

    except Exception as e:
        print("Error updating user data:", e)
    
    await start_handler(client, message)

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message):
    await help_handler(client, message)

@app.on_message(filters.command("return"))
async def return_command(client: Client, message):
    await start_handler(client, message)

@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats_cmd(client: Client, message):
    try:
        total_users = await mongo_db.get_total_users()
        total_uploads = await mongo_db.get_all_uploads()

        await message.reply(
            f"Bot Statistics:\n"
            f"Total Users: {total_users}\n"
            f"Total Uploads: {len(total_uploads)}"
        )
    except Exception as e:
        await message.reply("An error occurred while fetching statistics.")
        print(f"Error fetching stats: {e}")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_cmd(client: Client, message):
    if message.reply_to_message:
        reply_message = message.reply_to_message
        content = reply_message.caption if reply_message.caption else reply_message.text
        media = reply_message.photo if reply_message.photo else None
        
        await message.reply("Broadcasting message...")
        
        user_ids = await mongo_db.get_all_user_ids()

        for user_id in user_ids:
            try:
                if media:
                    await client.send_photo(user_id, media.file_id, caption=content)
                else:
                    await client.send_message(user_id, content)
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")

if __name__ == "__main__":
    time.sleep(10)

    retries = 5
    for attempt in range(retries):
        try:
            app.run()
            break
        except Exception as e:
            print(f"Error: {e}. Attempt {attempt + 1} of {retries}")
            time.sleep(5)
