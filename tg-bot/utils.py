from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from db_interactor import JsonLoader

json_loader = JsonLoader()


def generatePaintingSelectionTextButtons(user_favourites: list, page: int = 0):
    user_favourites.reverse()
    text = 'Список понравившихся:\n\n'

    keyboard = []

    if len(user_favourites) > 0:
        paints_after = len(user_favourites) - 5 * page
        for i in range(5 * page, 5 * page + min(paints_after, 5)):
            paint_data = json_loader.getPaintingData(user_favourites[i])
            text += f'{(i - 5 * page + 1) % 6}. *{paint_data["name"]}*\nАвтор: *{paint_data["author"]}*\n\n'

        first_row_len = 1
        pg_amount = (len(user_favourites) // 5)
        # checking if we need pagination
        if len(user_favourites) > 5:
            if page < pg_amount:
                keyboard.append([
                    InlineKeyboardButton('>> Следующая страница >>',
                                         callback_data=f'next_pg_{page+1}')
                ])
            if page > 0:
                keyboard.append([
                    InlineKeyboardButton('<< Предыдущая страница <<',
                                         callback_data=f'next_pg_{page-1}')
                ])
            text += f'(Страница {page+1} из {len(user_favourites) // 5 + 1})'

        if 2 <= paints_after <= 4:
            first_row_len = 2
        elif paints_after >= 5:
            first_row_len = 3

        first_row = []
        for i in range(first_row_len):
            first_row.append(InlineKeyboardButton(
                f'🏞 {str(i + 1)}', callback_data=f'pnt_btn_{user_favourites[page * 5 + i]}'))
        keyboard.append(first_row)

        second_row = []
        for i in range((min(paints_after, 5) - first_row_len)):
            second_row.append(InlineKeyboardButton(f'🏞 {str(first_row_len + i + 1)}',
                                                   callback_data=f'pnt_btn_{user_favourites[page * 5 + first_row_len + i]}'))
        if len(second_row) > 0:
            keyboard.append(second_row)

    else:
        text += 'Упс, тут ничего нет...Отправь мне фото картины, тогда сможешь добавить ее в избранные'

    keyboard.append([InlineKeyboardButton('🚫 Закрыть меню', callback_data='close_fav')])

    return text, InlineKeyboardMarkup(keyboard)


def generateSettingsTextButtons(user_settings: dict, favourites_number: int):
    text = '⚙️ *Настройки*\n\nРегулярные вопросы: ' + \
        ('🔔 включены' if user_settings['recurringEnabled'] else '🔕 выключены')
    if user_settings['recurringEnabled']:
        text += '\nКоличество вопросов в день: ' + str(user_settings['recurringTimesPerDay'])

    text += '\n\nПонравившиеся картины: ' + str(favourites_number)

    keyboard = []
    if user_settings['recurringEnabled']:
        keyboard.append([
            InlineKeyboardButton('🔕 Выключить регулярные вопросы', callback_data='on_off_quizes'),
            InlineKeyboardButton('Частота вопросов...', callback_data='change_freq')
        ])
    else:
        keyboard.append([
            InlineKeyboardButton('🔔 Включить регулярные вопросы', callback_data='on_off_quizes'),
        ])
    keyboard.append([
        InlineKeyboardButton('🗑 Сбросить список понравившихся картин', callback_data='reset_favs')
    ])

    return text, InlineKeyboardMarkup(keyboard)


def generatePaintingTextButtons(painting_id: int, user_id: int, full_text: bool = False,
                                raw_buttons: bool = False, quizStatus: str = 'none'):
    paint_data = json_loader.getPaintingData(painting_id)
    text = ''

    if quizStatus == 'True':
        text += '🎉 Правильно!\n\n'
    elif quizStatus == 'False':
        text += '😣 Неверно...\n\n'

    text += (f'*Название:* {paint_data["name"]}\n' +
             f'*Автор:* {paint_data["author"]}\n' +
             f'*Год создания:* {paint_data["date"]}\n' +
             f'*Страна*: {paint_data["country"]}\n')

    keyboard: list

    favourites = json_loader.getFavouritesData()
    if painting_id not in favourites[str(user_id)]:
        keyboard = [[InlineKeyboardButton(
            '❤️ Добавить в избранное',
            callback_data=f'add_to_favourites, {painting_id}')]]
    else:
        keyboard = [[InlineKeyboardButton(
            '💔 Удалить из избранных',
            callback_data=f'delete_from_favourites, {painting_id}')]]

    if 'text_info' in paint_data and len(text + f'\n\n{paint_data["text_info"]}') < 1024:
        if full_text:
            text += f'\n\n{paint_data["text_info"]}'
            keyboard.append([
                InlineKeyboardButton('📜 Свернуть описание',
                                     callback_data=f"{quizStatus} close_full_info_{painting_id}")
            ]
            )
        else:
            text += '...'
            keyboard.append([
                InlineKeyboardButton('📜 Развернуть описание',
                                     callback_data=f"{quizStatus} open_full_info_{painting_id}")
            ]
            )
    else:
        try:
            keyboard.append(
                [
                    InlineKeyboardButton('Узнать больше', url=f'{paint_data["url"]}')
                ]
            )
        # handling possible exception if no url with more info was found
        except Exception as e:
            pass

    if quizStatus != 'none':
        keyboard.append([InlineKeyboardButton('🔄 Новый вопрос', callback_data="anotherQuestion")])

    return text, (InlineKeyboardMarkup(keyboard) if not raw_buttons else keyboard)
