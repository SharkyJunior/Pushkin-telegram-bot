# from peewee import MySQLDatabase
from dotenv import load_dotenv
import os
import random
import json

load_dotenv()


class JsonLoader:
    def __init__(self):
        self.painting_data = json.load(open(os.getenv('PAINTINGS_INFO_PATH')))
        self.quiz_data = json.load(open(os.getenv('QUIZ_INFO_PATH')))
        self.settings_data = json.load(open(os.getenv('SETTINGS_DATA_PATH')))
        self.class_amt = len(self.painting_data)
        self.favourites = json.load(
            open(os.getenv('FAVOURITES_DATA_PATH')))

    def getPaintingData(self, painting_index: int) -> dict:
        self.painting_data = json.load(open(os.getenv('PAINTINGS_INFO_PATH')))
        return self.painting_data[painting_index]

    def getQuizData(self, user_id: int) -> int:
        self.quiz_data = json.load(open(os.getenv('QUIZ_INFO_PATH')))
        return self.quiz_data[str(user_id)]

    def getSettingsData(self) -> dict:
        self.settings_data = json.load(open(os.getenv('SETTINGS_DATA_PATH')))
        return self.settings_data

    def updateSettingsData(self, settings_data: dict) -> None:
        json.dump(settings_data, open(os.getenv('SETTINGS_DATA_PATH'), 'w'))

    def getFavouritesData(self) -> dict:
        self.favourites = json.load(
            open(os.getenv('FAVOURITES_DATA_PATH')))
        return self.favourites

    def updateFavouritesData(self, favourites: dict) -> None:
        json.dump(favourites, open(
            os.getenv('FAVOURITES_DATA_PATH'), 'w'))


# def returnRandomExhibitInfo():
#     mydb = MySQLDatabase('mysql', user='root', password=os.getenv('DB_PASS'),
#                          host='localhost', port=3306)
#     cur = mydb.cursor()
#     cur.execute('SELECT id FROM artwork_fromwebsite')
#     results = cur.fetchall()
#     idlist = list(i[0] for i in results)

#     cur.execute(
#         f"SELECT * FROM artwork_fromwebsite WHERE id={idlist[random.randint(0, 10000)]};"
#     )
#     exh = cur.fetchall()[0]

#     print(exh[1])
#     print(exh[5])
#     print(exh[10])

#     mydb.close()

#     return [exh[1], exh[5], exh[10], exh[14]]
