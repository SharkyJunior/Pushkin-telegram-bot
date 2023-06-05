from datetime import datetime
import pathlib
import logging
import asyncio
from functools import wraps


from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, MessageHandler,
                          filters, ContextTypes, CommandHandler)
from telegram import (Update, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.constants import ChatAction
from model_operator import ModelOperator
from db_interactor import JsonLoader
import os


load_dotenv()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# decorator that shows user that bot is typing something
def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(update, context, *args, **kwargs):
        await context.bot.send_chat_action(chat_id=update.effective_message.chat_id,
                                           action=ChatAction.TYPING)
        return await func(update, context,  *args, **kwargs)

    return command_func


app = ApplicationBuilder().token(os.getenv('BOT_API_KEY')).build()
bot = app.bot
op = ModelOperator()
json_loader = JsonLoader()

script_path = str(pathlib.Path(__file__).parent.resolve())

f = open(script_path + '/texts/notPhotoText.txt', encoding='utf-8')
notPhotoText = f.read()
f = open(script_path + '/texts/startText.txt', encoding='utf-8')
startText = f.read()


@send_typing_action
async def handlePhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    new_file = await bot.get_file(photo_id)
    filename = f'{datetime.now().strftime("%Y-%-m-%-d-%H:%M:%S:%f")}.jpg'

    photo_path = script_path + f'/pictures/cache/{filename}'

    downloaded_file = await new_file.download_to_drive(custom_path=photo_path)

    int_output = op.classify(str(downloaded_file))

    if int_output != -1:
        paint_data = json_loader.getData(int_output)

        text = (f'*Название:* {paint_data["name"]}\n' +
                f'*Автор:* {paint_data["author"]}\n' +
                f'*Год создания:* {paint_data["date"]}')

        await asyncio.sleep(1)
        try:
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    'Узнай больше', url=f'{paint_data["url"]}')
            ]])
            await update.message.reply_text(text, reply_markup=keyboard,
                                            parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await asyncio.sleep(1)
        await update.message.reply_text('Мне кажется, на этой фотке нет экспоната, который я знаю :( Попробуй еще раз')


async def handleNotPhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(notPhotoText)


@send_typing_action
async def handleStart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(1)
    await update.message.reply_text((f'Привет, {update.message.from_user.full_name}, ' + startText))

if __name__ == '__main__':
    app.add_handler(CommandHandler('start', handleStart))

    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE, handlePhotos))

    app.add_handler(MessageHandler(~filters.PHOTO, handleNotPhotos))

    app.run_polling()
