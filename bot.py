from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
import os
import logging
import pathlib

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = ApplicationBuilder().token(os.getenv('API_KEY')).build()
bot = app.bot()

script_path = pathlib.Path(__file__).parent.resolve()


async def handlePhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo.file_id
    new_file = await bot.get_file(photo_id)
    await new_file.download_to_drive(custom_path=(script_path + '/pictures/cache/'))


if __name__ == '__main__':
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE, handlePhotos))

    app.run_polling()
