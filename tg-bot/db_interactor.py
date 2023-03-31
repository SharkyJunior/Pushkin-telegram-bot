from peewee import MySQLDatabase
from dotenv import load_dotenv
import os
import random

load_dotenv()


def returnRandomExhibitInfo():
    mydb = MySQLDatabase('mysql', user='root', password=os.getenv('DB_PASS'),
                         host='localhost', port=3306)
    cur = mydb.cursor()
    cur.execute('SELECT id FROM artwork_fromwebsite')
    results = cur.fetchall()
    idlist = list(i[0] for i in results)

    cur.execute(
        f"SELECT * FROM artwork_fromwebsite WHERE id={idlist[random.randint(0, 10000)]};"
    )
    exh = cur.fetchall()[0]

    print(exh[1])
    print(exh[5])
    print(exh[10])

    mydb.close()

    return [exh[1], exh[5], exh[10], exh[14]]
