from pyrogram import Client, filters, types  # Import types for InlineKeyboardMarkup
from config import BOT_IMAGE_URL

async def start_handler(client: Client, message):
    bot_image_url = BOT_IMAGE_URL
    
    # Define buttons using InlineKeyboardButton
    buttons = [
        [
            types.InlineKeyboardButton("Updates", url="https://t.me/Thealphabotz"),
            types.InlineKeyboardButton("Support", url="https://t.me/thealphabotz")
        ],
        [
            types.InlineKeyboardButton("Help", callback_data="help"),
            types.InlineKeyboardButton("Source", url="https://github.com/utkarshdubey2008/imagehost")
        ]
    ]
    
    # Create InlineKeyboardMarkup from the buttons
    reply_markup = types.InlineKeyboardMarkup(buttons)

    await message.reply_photo(
        photo=bot_image_url,
        caption=(
            "Welcome to ImageHost Bot! Send me an image, and I'll upload it for you.\n\n"
            "I can help you host your images and provide you with a shareable link.\n"
            "Feel free to reach out if you have any questions!"
        ),
        reply_markup=reply_markup  # Use the InlineKeyboardMarkup instance here
    )
