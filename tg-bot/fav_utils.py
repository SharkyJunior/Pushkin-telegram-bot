from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from db_interactor import JsonLoader

json_loader = JsonLoader()


def generatePaintingSelectionTextButtons(user_favourites: list, page: int = 0):
    user_favourites.reverse()
    text = 'Список понравившихся:\n\n'

    paints_after = len(user_favourites) - 5 * page
    for i in range(5 * page, 5 * page + min(paints_after, 5)):
        paint_data = json_loader.getPaintingData(user_favourites[i])
        text += f'{(i - 5 * page + 1) % 6}. *{paint_data["name"]}*\nАвтор: *{paint_data["author"]}*\n\n'

    keyboard = []

    first_row_len = 1
    pg_amount = (len(user_favourites) // 5)
    # checking if we need pagination
    if len(user_favourites) > 5:
        if page < pg_amount:
            keyboard.append([
                InlineKeyboardButton('>> Следующая страница >>', callback_data=f'next_pg_{page+1}')
            ])
        if page > 0:
            keyboard.append([
                InlineKeyboardButton('<< Предыдущая страница <<', callback_data=f'next_pg_{page-1}')
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

    keyboard.append([InlineKeyboardButton('🚫 Закрыть меню', callback_data='close_fav')])

    return text, InlineKeyboardMarkup(keyboard)
