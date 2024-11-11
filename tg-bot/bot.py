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
from utils import (generatePaintingSelectionTextButtons,
                   generateSettingsTextButtons, generatePaintingTextButtons)
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

script_path = str(pathlib.Path(__file__).parent.resolve())

f = open(script_path + '/texts/notPhotoText.txt', encoding='utf-8')
notPhotoText = f.read()
f = open(script_path + '/texts/startText.txt', encoding='utf-8')
startText = f.read()
f = open(script_path + '/texts/afterFirstQuiz.txt', encoding='utf-8')
afterFirstQuiz = f.read()

opened_favourites = {}
opened_settings = {}


hours_to_send_quizes = {
    "1": [9],
    "2": [9, 20],
    "3": [9, 15, 20],
    "4": [9, 12, 16, 20],
}


@send_typing_action
async def handlePhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    new_file = await bot.get_file(photo_id)
    filename = f'{datetime.now().strftime("%Y-%-m-%-d-%H:%M:%S:%f")}.jpg'

    photo_path = script_path + f'/pictures/cache/{filename}'

    downloaded_file = await new_file.download_to_drive(custom_path=photo_path)

    int_output = op.classify(str(downloaded_file))

    if int_output != -1:
        text, keyboard = generatePaintingTextButtons(int_output, update.effective_user.id)

        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown",
                                        reply_to_message_id=update.message.id)
    else:
        await update.message.reply_text(
            'Мне кажется, на этой фотографии нет экспоната, который я знаю :(\nПопробуйте еще раз',
            reply_to_message_id=update.message.id
        )


async def handleNotPhotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(notPhotoText)


@send_typing_action
async def handleStart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"USER_ID: {update.message.from_user.id}")
    print(f"CHAT_ID: {update.effective_chat.id}")
    await asyncio.sleep(1)

    favourites = json_loader.getFavouritesData()

    # if user is talking to bot for the first time
    settings_data = json_loader.getSettingsData()
    user_id = str(update.message.from_user.id)
    if user_id not in settings_data:
        settings_data[user_id] = {
            'recurringEnabled': False,
            'recurringTimesPerDay': 1,
            'quizNotPlayed': True,
        }
        json_loader.updateSettingsData(settings_data)
    if user_id not in favourites:
        favourites[user_id] = []
        json_loader.updateFavouritesData(favourites)

    await update.message.reply_text(
        (f'Привет, {update.message.from_user.full_name}, ' + startText))


# TODO: make settings menu dynamic (it changes depending on user settings)
async def handleSettings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) not in opened_settings:
        user_settings = json_loader.getSettingsData()[str(user_id)]
        user_favorites = json_loader.getFavouritesData()[str(user_id)]

        text, keyboard = generateSettingsTextButtons(user_settings, len(user_favorites))

        settings_menu = await update.message.reply_text(text, reply_markup=keyboard,
                                                        parse_mode="Markdown")
        opened_settings[str(update.effective_user.id)] = settings_menu.id
    else:
        try:
            error_message = await context.bot.send_message(
                user_id, '👆 Настройки уже открыты 👆',
                reply_to_message_id=opened_settings[str(user_id)])
            await asyncio.sleep(10)
            await error_message.delete()
        except Exception:
            opened_settings.pop(str(update.message.from_user.id), None)
            await handleSettings(update, context)


@send_typing_action
async def handleQuizCmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image_path, keyboard = quiz.generateQuizData()

    await update.message.reply_photo(image_path, caption="Кто написал эту картину?",
                                     reply_markup=keyboard)


@send_typing_action
async def handleShowFavourites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    user_favourites: list = json_loader.getFavouritesData()[str(user_id)]

    if str(user_id) not in opened_favourites:
        text, keyboard = generatePaintingSelectionTextButtons(user_favourites)

        favorites_list = await update.message.reply_text(text, reply_markup=keyboard,
                                                         parse_mode="Markdown")
        opened_favourites[str(user_id)] = [favorites_list.id, 0]
    else:
        try:
            error_message = await context.bot.send_message(
                user_id, '👆 У тебя уже есть открытый список понравившихся 👆',
                reply_to_message_id=opened_favourites[str(user_id)][0])
        except Exception:
            opened_favourites.pop(str(update.message.from_user.id), None)
            await handleShowFavourites(update, context)


async def handleCallBack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.callback_query.data
    settings_data = json_loader.getSettingsData()
    favourites = json_loader.getFavouritesData()
    user_id = update.effective_user.id

    # handling quiz answers
    if re.match(r'^[01]{1} [\d]{1,}$', user_answer):
        data = [int(i) for i in user_answer.split()]
        print(data)
        quiz_status = True if data[0] == 1 else False

        paint_data = json_loader.getPaintingData(data[1])
        text, keyboard = generatePaintingTextButtons(
            data[1], user_id, raw_buttons=True, quizStatus=str(quiz_status))

        keyboard.append(
            [
                InlineKeyboardButton('🚫 Закрыть', callback_data='close')
            ]
        )

        if quiz_status:
            await update.callback_query.edit_message_caption(text,
                                                             reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await update.callback_query.edit_message_caption(text,
                                                             reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        # recurring quizes prompt after first time playing quiz
        if settings_data[str(update.callback_query.from_user.id)]['quizNotPlayed']:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('Да, я хочу больше вопросов!',
                                             callback_data="firstQuiz_yes")
                    ],
                    [
                        InlineKeyboardButton('Нет, спасибо.',
                                             callback_data="firstQuiz_no")
                    ]
                ]
            )
            await bot.send_message(update.effective_chat.id,
                                   afterFirstQuiz, reply_markup=keyboard)
            settings_data[str(update.callback_query.from_user.id)
                          ]['quizNotPlayed'] = False
            json_loader.updateSettingsData(settings_data)

    elif user_answer == 'anotherQuestion':
        image_path, keyboard = quiz.generateQuizData()

        await context.bot.send_photo(user_id, image_path, caption="Кто написал эту картину?",
                                     reply_markup=keyboard)

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
            'Хорошо. Если передумаешь - включай регулярные вопросы в настройках (/settings)',
            reply_markup=None)

    elif re.match(r'^first_timesPerDay-[\d]{1}$', user_answer) is not None:
        settings_data[str(update.callback_query.from_user.id)
                      ]['recurringTimesPerDay'] = int(user_answer[-1])

        json_loader.updateSettingsData(settings_data)

        await update.callback_query.edit_message_text(
            'Все, теперь я буду присылать регулярные вопросы.', reply_markup=None)
        await asyncio.sleep(5)
        await update.callback_query.delete_message()

    elif re.match(r'^timesPerDay-[\d]{1}$', user_answer) is not None:
        settings_data[str(update.callback_query.from_user.id)
                      ]['recurringTimesPerDay'] = int(user_answer[-1])

        json_loader.updateSettingsData(settings_data)
        await update.callback_query.answer('✅ Сохранено')

        text, keyboard = generateSettingsTextButtons(
            settings_data[str(user_id)], len(favourites[str(user_id)]))

        await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                      parse_mode='Markdown')

    elif 'add_to_favourites' in user_answer:
        int_op = int(user_answer[user_answer.find(",") + 1:])
        user_id = update.effective_user.id
        if int_op not in favourites[str(user_id)]:
            favourites[str(user_id)].append(int_op)
        json_loader.updateFavouritesData(favourites)
        if str(user_id) in opened_favourites:
            user_favorites = favourites[str(user_id)]
            fav_list = opened_favourites[str(user_id)]

            text, keyboard = generatePaintingSelectionTextButtons(user_favorites, fav_list[1])

            try:
                await context.bot.edit_message_text(text, user_id, fav_list[0],
                                                    reply_markup=keyboard,
                                                    parse_mode='Markdown')
            except Exception:
                pass

        await update.callback_query.answer('✅ Добавлено в избранные')

        paint_data = json_loader.getPaintingData(int_op)
        keyboard = [
            [
                InlineKeyboardButton('💔 Удалить из избранных',
                                     callback_data=f'delete_from_favourites, {int_op}')
            ],
        ]

        for i in range(3):
            try:
                keyboard.append([
                    update.callback_query.message.reply_markup.inline_keyboard[i+1][0]
                ])
            except Exception:
                pass

        await update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))

    elif 'delete_from_favourites' in user_answer:
        int_op = int(user_answer[user_answer.find(",") + 1:])
        favourites[str(user_id)].remove(int_op)
        json_loader.updateFavouritesData(favourites)
        if str(user_id) in opened_favourites:
            user_favorites = favourites[str(user_id)]
            fav_list = opened_favourites[str(user_id)]

            text, keyboard = generatePaintingSelectionTextButtons(user_favorites, fav_list[1])

            try:
                await context.bot.edit_message_text(text, user_id, fav_list[0],
                                                    reply_markup=keyboard,
                                                    parse_mode='Markdown')
            except Exception:
                pass
        await update.callback_query.answer('✅ Удалено из избранных')

        paint_data = json_loader.getPaintingData(int_op)
        keyboard = [
            [
                InlineKeyboardButton('❤️ Добавить в избранные',
                                     callback_data=f'add_to_favourites, {int_op}')
            ],
        ]

        for i in range(3):
            try:
                keyboard.append([
                    update.callback_query.message.reply_markup.inline_keyboard[i+1][0]
                ])
            except Exception:
                pass

        await update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))

    elif 'close' in user_answer:
        if 'close_full_info' not in user_answer:
            await update.callback_query.delete_message()
            if user_answer == 'close_fav':
                opened_favourites.pop(str(update.callback_query.from_user.id), None)
        else:
            painting_id = int(user_answer[user_answer.rfind('_')+1:])

            try:
                text, keyboard = generatePaintingTextButtons(painting_id, user_id)
                await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                              parse_mode='Markdown')
            except Exception:
                text, keyboard = generatePaintingTextButtons(painting_id, user_id, raw_buttons=True)
                if 'True' in user_answer:
                    text, keyboard = generatePaintingTextButtons(
                        painting_id, user_id, quizStatus='True', raw_buttons=True)

                elif 'False' in user_answer:
                    text, keyboard = generatePaintingTextButtons(
                        painting_id, user_id, quizStatus='False', raw_buttons=True)

                keyboard.append([
                    InlineKeyboardButton('🚫 Закрыть', callback_data='close')
                ])
                keyboard = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_caption(text, reply_markup=keyboard,
                                                                 parse_mode='Markdown')

    elif 'open_full_info' in user_answer:
        painting_id = int(user_answer[user_answer.rfind('_')+1:])

        try:
            text, keyboard = generatePaintingTextButtons(painting_id, user_id, True)
            await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                          parse_mode='Markdown')
        except Exception:
            text, keyboard = generatePaintingTextButtons(
                painting_id, user_id, True, raw_buttons=True)
            if 'True' in user_answer:
                text, keyboard = generatePaintingTextButtons(
                    painting_id, user_id, True, quizStatus='True', raw_buttons=True)
            elif 'False' in user_answer:
                text, keyboard = generatePaintingTextButtons(
                    painting_id, user_id, True, quizStatus='False', raw_buttons=True)
            keyboard.append([
                InlineKeyboardButton('🚫 Закрыть', callback_data='close')
            ])
            keyboard = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_caption(text, reply_markup=keyboard,
                                                             parse_mode='Markdown')

    elif re.match(r'^pnt_btn_[\d]{1,}$', user_answer) is not None:
        painting_id = int(user_answer[user_answer.rfind('_')+1:])
        paint_data = json_loader.getPaintingData(painting_id)
        image_path = os.path.join(os.getenv("QUIZ_IMAGES_PATH"), f'{painting_id}.jpg')

        text, keyboard = generatePaintingTextButtons(painting_id, user_id, raw_buttons=True)
        keyboard.append([
            InlineKeyboardButton('🚫 Закрыть', callback_data='close')
        ])

        await context.bot.send_photo(update.effective_user.id, image_path, text,
                                     reply_markup=InlineKeyboardMarkup(keyboard),
                                     parse_mode='Markdown')

    elif re.match(r'^next_pg_[\d]{1,}$', user_answer) is not None:
        next_pg = int(re.findall(r'\d+', user_answer)[0])
        user_favorites = json_loader.getFavouritesData()[str(update.effective_user.id)]

        text, keyboard = generatePaintingSelectionTextButtons(user_favorites, next_pg)

        await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                      parse_mode='Markdown')
        opened_favourites[str(user_id)][1] = next_pg

    elif user_answer == 'reset_favs':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Да, сбросить', callback_data='reset_yes'),
            ],
            [
                InlineKeyboardButton('Нет, оставить', callback_data='back_settings'),
            ]
        ])

        text = '🛑 *Внимание* 🛑\nТы действительно хочешь *сбросить* список понравившихся картин?'
        await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                      parse_mode='Markdown')

    elif user_answer == 'reset_yes':
        favourites[str(user_id)] = []
        json_loader.updateFavouritesData(favourites)
        await update.callback_query.answer('✅ Список сброшен', show_alert=True)

        text, keyboard = generateSettingsTextButtons(settings_data[str(user_id)], 0)

        await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                      parse_mode='Markdown')

    elif user_answer == 'back_settings':
        text, keyboard = generateSettingsTextButtons(
            settings_data[str(user_id)], len(favourites[str(user_id)]))

        await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                      parse_mode='Markdown')

    elif user_answer == 'on_off_quizes':
        settings_data[str(user_id)]['recurringEnabled'] = not settings_data[str(
            user_id)]['recurringEnabled']
        json_loader.updateSettingsData(settings_data)

        text, keyboard = generateSettingsTextButtons(
            settings_data[str(user_id)], len(favourites[str(user_id)]))

        await update.callback_query.edit_message_text(text, reply_markup=keyboard,
                                                      parse_mode='Markdown')

    elif user_answer == 'change_freq':
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        '1 раз в день', callback_data="timesPerDay-1"),
                    InlineKeyboardButton(
                        '2 раза в день', callback_data="timesPerDay-2")
                ],
                [
                    InlineKeyboardButton(
                        '3 раза в день', callback_data="timesPerDay-3"),
                    InlineKeyboardButton(
                        '4 раза в день', callback_data="timesPerDay-4")
                ]
            ]
        )

        await update.callback_query.edit_message_text('⚙️ *Настройки*\n\nВыберите опцию:',
                                                      reply_markup=keyboard,
                                                      parse_mode='Markdown')


async def callback_time(context: ContextTypes.DEFAULT_TYPE):
    settings_data = json_loader.getSettingsData()
    current_time = datetime.now()
    print('-' * 30)
    print('Time to ping - ' + current_time.strftime('%H:%M:%S'))

    # collecting all periods we need to ping based on the current hour
    periods_to_ping = []
    for i in range(1, len(hours_to_send_quizes) + 1):
        if current_time.hour in hours_to_send_quizes[str(i)]:
            periods_to_ping.append(i)
    print('Periods to ping: ' + ', '.join([str(i) for i in periods_to_ping]) + '\n')

    # pinging all users who opted in recurring quizes
    for user_id, user_data in settings_data.items():
        if (user_data['recurringEnabled']
                and user_data['recurringTimesPerDay'] in periods_to_ping):
            image_path, keyboard = quiz.generateQuizData()

            # if user has blocked the bot, then catching exception
            try:
                await context.bot.send_photo(chat_id=user_id,
                                             caption='Кто написал эту картину?',
                                             photo=image_path,
                                             reply_markup=keyboard)
                print(f'[i] Sent quiz to user {user_id}')
            except Exception:
                print(f'[!] Failed to send quiz to user {user_id}')

    print('-' * 30)


def count_min_sec_remainder() -> int:
    now = datetime.now()
    return (59-now.minute, 60-now.second)

    # mins1 = (33-current_dateTime.hour) * 60
    # mins2 = 60-current_dateTime.minute
    # global firstwork
    # firstwork = (mins1+mins2) * 60


if __name__ == '__main__':
    # job_queue = app.job_queue
    # delta = count_min_sec_remainder()
    # jobdelta = timedelta(minutes=delta[0], seconds=delta[1])
    # print(f'Time delta: {delta[0]}m {delta[1]}s\n' + '-' * 30)
    # job_minute = job_queue.run_repeating(
    #     callback_time, interval=60*60, first=jobdelta)

    # job_queue.start()

    app.add_handler(CallbackQueryHandler(handleCallBack))

    app.add_handler(CommandHandler('start', handleStart))
    app.add_handler(CommandHandler('settings', handleSettings))
    app.add_handler(CommandHandler('question', handleQuizCmd))
    app.add_handler(CommandHandler('favourites', handleShowFavourites))

    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE, handlePhotos))

    app.add_handler(MessageHandler(
        ~filters.PHOTO & ~filters.COMMAND, handleNotPhotos))

    app.run_polling()
