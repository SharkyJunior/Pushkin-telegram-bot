import db_interactor
import random

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
