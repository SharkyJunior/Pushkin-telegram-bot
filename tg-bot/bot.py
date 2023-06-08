from datetime import datetime, timedelta
import pathlib
import logging
import asyncio
import random
import json
import re

from functools import wraps


from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, MessageHandler,
                          filters, ContextTypes, CommandHandler,
                          CallbackQueryHandler)
from telegram import (Update, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.constants import ChatAction
from model_operator import ModelOperator
from db_interactor import JsonLoader
import quiz
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
        await context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id,
            action=ChatAction.TYPING)
        return await func(update, context,  *args, **kwargs)

    return command_func


app = ApplicationBuilder().token(os.getenv('BOT_API_KEY')).build()
bot = app.bot
op = ModelOperator()
json_loader = JsonLoader()
ongoing_quizes = {}

script_path = str(pathlib.Path(__file__).parent.resolve())

f = open(script_path + '/texts/notPhotoText.txt', encoding='utf-8')
notPhotoText = f.read()
f = open(script_path + '/texts/startText.txt', encoding='utf-8')
startText = f.read()
f = open(script_path + '/texts/afterFirstQuiz.txt', encoding='utf-8')
afterFirstQuiz = f.read()

id_list = []
firstwork = 0


@send_typing_action
async def handlePhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    new_file = await bot.get_file(photo_id)
    filename = f'{datetime.now().strftime("%Y-%-m-%-d-%H:%M:%S:%f")}.jpg'

    photo_path = script_path + f'/pictures/cache/{filename}'

    downloaded_file = await new_file.download_to_drive(custom_path=photo_path)

    int_output = op.classify(str(downloaded_file))

    if int_output != -1:
        paint_data = json_loader.getPaintingData(int_output)

        text = (f'*Название:* {paint_data["name"]}\n' +
                f'*Автор:* {paint_data["author"]}\n' +
                f'*Год создания:* {paint_data["date"]}')

        await asyncio.sleep(1)

        keyboard = [[InlineKeyboardButton(
            'Добавить в избранное',
            callback_data='add_to_favourites')]]

        # handling possible exception if no url with more info was found
        try:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        'Узнать больше', url=f'{paint_data["url"]}')
                ]
            )
        except Exception as e:
            pass

        await update.message.reply_text(text, reply_markup=keyboard,
                                        parse_mode="Markdown")
    else:
        await asyncio.sleep(1)
        await update.message.reply_text(
            'Мне кажется, на этой фотографии нет экспоната, который я знаю :('
            + '\nПопробуйте еще раз'
        )


async def handleNotPhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(notPhotoText)


@send_typing_action
async def handleStart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(1)

    id_list.append(update.effective_chat.id)

    # if user is talking to bot for the first time
    settings_data = json_loader.getSettingsData()
    user_id = str(update.message.from_user.id)
    if user_id not in settings_data:
        settings_data[user_id] = {
            'recurringEnabled': False,
            'recurringTimesPerDay': 1,
            'quizHardMode': True,
            'quizNotPlayed': True,
        }
        json_loader.updateSettingsData(settings_data)

    await update.message.reply_text(
        (f'Привет, {update.message.from_user.full_name}, ' + startText))
    # current_dateTime = datetime.now()
    # while True:
    #     if (current_dateTime.minute == 0):  # current_dateTime.hour == 10
    #         await bot.send_message(chat_id=update.effective_chat.id,
    #                                text='Hello')
    #         await asyncio.sleep(60)
    #     else:
    #         await asyncio.sleep(60)
    #     current_dateTime = datetime.now()


@send_typing_action
async def handleQuizCmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    painting_index = random.randint(0, json_loader.class_amt-1)

    image_path = os.path.join(
        os.getenv("QUIZ_IMAGES_PATH"), f'{painting_index}.jpg')

    correctArtist, falseArtists = quiz.generateArtistAnswers(painting_index)

    answer_pool = [correctArtist]
    answer_pool.extend(falseArtists)
    random.shuffle(answer_pool)
    correctIndex = answer_pool.index(correctArtist)

    ongoing_quizes[str(update.message.from_user.id)] = [painting_index,
                                                        correctIndex]

    keyboard = [
        [
            InlineKeyboardButton(answer_pool[0], callback_data=0),
        ],
        [
            InlineKeyboardButton(answer_pool[1], callback_data=1),
        ],
        [
            InlineKeyboardButton(answer_pool[2], callback_data=2),
        ],
        [
            InlineKeyboardButton(answer_pool[3], callback_data=3),
        ]
    ]

    await update.message.reply_photo(image_path,
                                     caption="Кто написал эту картину?",
                                     reply_markup=InlineKeyboardMarkup(
                                         keyboard)
                                     )

    print(ongoing_quizes)


# TODO: make settings menu dynamic (it changes depending on user settings)
async def handleSettings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Включить регулярные вопросы')
        ]
    ])


async def handleCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.callback_query.data
    settings_data = json_loader.getSettingsData()

    # handling quiz answers
    if user_answer.isdigit():
        correct_answer = ongoing_quizes[str(
            update.callback_query.from_user.id)][1]

        paint_data = json_loader.getPaintingData(
            ongoing_quizes[str(update.callback_query.from_user.id)][0])
        if int(user_answer) == correct_answer:
            await update.callback_query.edit_message_caption(
                f"Правильный ответ! \nЭто *{paint_data['name']}*,"
                + f"автор - *{paint_data['author']}*",
                reply_markup=None, parse_mode="Markdown")
        else:
            await update.callback_query.edit_message_caption(
                f"Неверно :( \nАвтор этой картины - *{paint_data['author']}*."
                + f"Картина называется *{paint_data['name']}*",
                reply_markup=None, parse_mode="Markdown")

        await asyncio.sleep(1)

        # recurring quizes prompt after first time playing quiz
        if settings_data[str(update.callback_query.from_user.id)]['quizNotPlayed'] == True:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('Да, я хочу больше вопросов!',
                                             callback_data="firstQuiz_yes")
                    ],
                    [
                        InlineKeyboardButton(
                            'Нет, спасибо.', callback_data="firstQuiz_no")
                    ]
                ]
            )
            await bot.send_message(update.effective_chat.id,
                                   afterFirstQuiz, reply_markup=keyboard)
            settings_data[str(update.callback_query.from_user.id)
                          ]['quizNotPlayed'] = False
            json_loader.updateSettingsData(settings_data)

    elif user_answer == 'firstQuiz_yes':
        settings_data[str(update.callback_query.from_user.id)
                      ]['recurringEnabled'] = True
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('1 раз в день',
                                         callback_data="first_timesPerDay-1"),
                    InlineKeyboardButton(
                        '2 раза в день', callback_data="first_timesPerDay-2")
                ],
                [
                    InlineKeyboardButton('3 раза в день',
                                         callback_data="first_timesPerDay-3"),
                    InlineKeyboardButton(
                        '4 раза в день', callback_data="first_timesPerDay-4")
                ]
            ]
        )

        json_loader.updateSettingsData(settings_data)
        await update.callback_query.edit_message_text(
            'Хорошо, еще одна просьба. Укажи, сколько раз в день я должен отправлять тебе вопросы?',
            reply_markup=keyboard)

    elif user_answer == 'firstQuiz_no':
        await update.callback_query.edit_message_text(
            'Хорошо. Если передумаешь - включай регулярные вопросы в настройках (/settings)', reply_markup=None)

    elif re.match(r'^first_timesPerDay-[\d]{1}$', user_answer) is not None:
        settings_data[str(update.callback_query.from_user.id)
                      ]['recurringTimesPerDay'] = int(user_answer[-1])

        json_loader.updateSettingsData(settings_data)

        await update.callback_query.edit_message_text('Все, теперь я буду теперь присылать регулярные вопросы.', reply_markup=None)
        await asyncio.sleep(5)
        await update.callback_query.delete_message()

    elif user_answer == 'add_to_favourites':
        # favourites


async def callback_time(context: ContextTypes.DEFAULT_TYPE):
    for i in id_list:
        await context.bot.send_message(chat_id=i, text='message')


def count_min_sec_remainder() -> int:
    now = datetime.now()
    return (60-now.minute, 60-now.second)
    
    # mins1 = (33-current_dateTime.hour) * 60
    # mins2 = 60-current_dateTime.minute
    # global firstwork
    # firstwork = (mins1+mins2) * 60


if __name__ == '__main__':
    job_queue = app.job_queue
    delta = count_min_sec_remainder()
    firstwork = datetime.now() + timedelta(minutes=delta[0], seconds=delta[1])
    job_minute = job_queue.run_repeating(
        callback_time, interval=60*60, first=firstwork)  # 3*24*60*60
    
    app.add_handler(CallbackQueryHandler(handleCallback))

    app.add_handler(CommandHandler('start', handleStart))
    app.add_handler(CommandHandler('settings', handleSettings))
    app.add_handler(CommandHandler('quiz', handleQuizCmd))

    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE, handlePhotos))

    app.add_handler(MessageHandler(~filters.PHOTO, handleNotPhotos))

    app.run_polling()
