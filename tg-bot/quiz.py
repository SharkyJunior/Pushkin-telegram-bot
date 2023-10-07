import db_interactor
import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv

load_dotenv()

loader = db_interactor.JsonLoader()


def generateArtistAnswers(correct_painting_id: int):
    correct_artist = loader.getPaintingData(correct_painting_id)['author']

    unique_false_artists = []
    for painting in loader.painting_data:
        if (painting['author'] != correct_artist and
                painting['author'] not in unique_false_artists):
            unique_false_artists.append(painting['author'])

    random.shuffle(unique_false_artists)
    return correct_artist, unique_false_artists[:3]


def generateQuizData():
    painting_index = random.randint(0, loader.class_amt-1)

    image_path = os.path.join(
        os.getenv("QUIZ_IMAGES_PATH"), f'{painting_index}.jpg')

    correctArtist, falseArtists = generateArtistAnswers(painting_index)

    answer_pool = [correctArtist]
    answer_pool.extend(falseArtists)
    random.shuffle(answer_pool)
    correctIndex = answer_pool.index(correctArtist)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                answer_pool[0], callback_data=f"{'1' if correctIndex == 0 else '0'} {painting_index}"),
        ],
        [
            InlineKeyboardButton(
                answer_pool[1], callback_data=f"{'1' if correctIndex == 1 else '0'} {painting_index}"),
        ],
        [
            InlineKeyboardButton(
                answer_pool[2], callback_data=f"{'1' if correctIndex == 2 else '0'} {painting_index}"),
        ],
        [
            InlineKeyboardButton(
                answer_pool[3], callback_data=f"{'1' if correctIndex == 3 else '0'} {painting_index}"),
        ]
    ])

    return image_path, keyboard
