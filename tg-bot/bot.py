from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, MessageHandler,
                          filters, ContextTypes)
from telegram import Update
import os
import logging
import pathlib
from datetime import datetime

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = ApplicationBuilder().token(os.getenv('BOT_API_KEY')).build()
bot = app.bot

script_path = pathlib.Path(__file__).parent.resolve()


async def handlePhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    new_file = await bot.get_file(photo_id)
    filename = f'{datetime.now().strftime("%Y-%-m-%-d-%H:%M:%S:%f")}.jpg'

    photo_path = str(script_path) + f'/pictures/cache/{filename}'
   
    await new_file.download_to_drive(custom_path=photo_path)


if __name__ == '__main__':
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE, handlePhotos))

    app.run_polling()
