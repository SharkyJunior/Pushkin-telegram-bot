
from db_interactor import returnRandomExhibitInfo
from datetime import datetime
import pathlib
import logging

from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, MessageHandler,
                          filters, ContextTypes, CommandHandler)
from telegram import Update
from model_operator import ModelOperator
from db_interactor import JsonLoader
import os


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = ApplicationBuilder().token(os.getenv('BOT_API_KEY')).build()
bot = app.bot
op = ModelOperator()
json_loader = JsonLoader()

script_path = str(pathlib.Path(__file__).parent.resolve())

f = open(script_path + '/texts/notPhotoText.txt', encoding='utf-8')
notPhotoText = f.read()
f = open(script_path + '/texts/startText.txt', encoding='utf-8')
startText = f.read()


async def handlePhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    new_file = await bot.get_file(photo_id)
    filename = f'{datetime.now().strftime("%Y-%-m-%-d-%H:%M:%S:%f")}.jpg'

    photo_path = script_path + f'/pictures/cache/{filename}'

    downloaded_file = await new_file.download_to_drive(custom_path=photo_path)

    int_output = op.classify(str(downloaded_file))

    paint_data = json_loader.getData(int_output)

    await update.message.reply_text(f'Это "{paint_data["name"]}"\n\nАвтор: {paint_data["author"]}')

    # randInfo = returnRandomExhibitInfo()

    # caption = f'*Название*: {randInfo[0]} \n*Автор*: {randInfo[2]} \n*Год(-ы) создания*: {randInfo[3]}'
    # await update.message.reply_photo(randInfo[1], caption=caption, parse_mode='Markdown')


async def handleNotPhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(notPhotoText)


async def handleStart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text((f'Привет, {update.message.from_user.full_name}, ' + startText))

if __name__ == '__main__':
    app.add_handler(CommandHandler('start', handleStart))

    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE, handlePhotos))

    app.add_handler(MessageHandler(~filters.PHOTO, handleNotPhotos))

    app.run_polling()
