import pathlib

from telegram import Update, Bot
from telegram.ext import ContextTypes

script_path = pathlib.Path(__file__).parent.resolve()

async def handlePhotos(bot: Bot, update: Update,
                       context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo.file_id
    new_file = await bot.get_file(photo_id)
    await new_file.download_to_drive(custom_path=(script_path
                                                  + '/pictures/cache/')
                                     )
    
